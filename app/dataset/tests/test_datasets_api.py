from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Dataset

from dataset.serializers import DatasetSerializer


DATASETS_URL = reverse('dataset:dataset-list')


class PublicDatasetsApiTests(TestCase):
    """Test the publicly available datasets API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving datasets"""
        res = self.client.get(DATASETS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDatasetsApiTests(TestCase):
    """Test the authorized user datasets API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@me.com',
            'psswd123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_datasets(self):
        """Test retrieving datasets"""
        Dataset.objects.create(user=self.user, name='MNIST_chinese')
        Dataset.objects.create(user=self.user, name='MNIST_zalando')

        res = self.client.get(DATASETS_URL)

        datasets = Dataset.objects.all().order_by('-name')
        serializer = DatasetSerializer(datasets, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_datasets_limited_to_user(self):
        """Test that datasets returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@me.com',
            'testpass'
        )
        Dataset.objects.create(user=user2, name='MNIST')
        dataset = Dataset.objects.create(user=self.user, name='MNIST_extended')

        res = self.client.get(DATASETS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], dataset.name)

    def test_create_dataset_successful(self):
        """Test creating a new dataset"""
        payload = {'name': 'MNIST_chinese'}
        self.client.post(DATASETS_URL, payload)

        exists = Dataset.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_dataset_invalid(self):
        """Test creating a new dataset with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(DATASETS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
