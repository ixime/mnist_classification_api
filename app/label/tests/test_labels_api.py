from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Label

from label.serializers import LabelSerializer


LABELS_URL = reverse('label:label-list')


class PublicLabelsApiTests(TestCase):
    """Test the publicly available labels API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving labels"""
        res = self.client.get(LABELS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLabelsApiTests(TestCase):
    """Test the authorized user labels API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@me.com',
            'psswd123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_labels(self):
        """Test retrieving labels"""
        Label.objects.create(user=self.user, name='Shirt')
        Label.objects.create(user=self.user, name='Cat')

        res = self.client.get(LABELS_URL)

        labels = Label.objects.all().order_by('-name')
        serializer = LabelSerializer(labels, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_labels_limited_to_user(self):
        """Test that labels returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@me.com',
            'testpass'
        )
        Label.objects.create(user=user2, name='dog')
        label = Label.objects.create(user=self.user, name='pants')

        res = self.client.get(LABELS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], label.name)

    def test_create_label_successful(self):
        """Test creating a new label"""
        payload = {'name': 'flower'}
        self.client.post(LABELS_URL, payload)

        exists = Label.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_label_invalid(self):
        """Test creating a new label with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(LABELS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
