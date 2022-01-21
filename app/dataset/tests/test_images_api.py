from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Image, Label, Csvfile

from dataset.serializers import ImageSerializer


IMAGES_URL = reverse('dataset:image-list')


class PublicImagesApiTests(TestCase):
    """Test the publicly available images API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving datasets"""
        res = self.client.get(IMAGES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateImagesApiTests(TestCase):
    """Test the authorized user images API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@me.com',
            'psswd123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.label = Label.objects.create(user=self.user, name='cat')
        self.csvfile = Csvfile.objects.create(user=self.user,
                                              name='MNIST_train',
                                              labelcol=0,
                                              imgcolstart=1,
                                              imgcolend=16
                                              )

    def test_retrieve_images(self):
        """Test retrieving images"""
        Image.objects.create(user=self.user,
                             name='MNIST_chinese',
                             csvfile=self.csvfile,
                             row=0,
                             label=self.label
                             )
        Image.objects.create(user=self.user,
                             name='MNIST_zalando',
                             csvfile=self.csvfile,
                             row=16,
                             label=self.label
                             )

        res = self.client.get(IMAGES_URL)

        images = Image.objects.all().order_by('-name')
        serializer = ImageSerializer(images, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_images_limited_to_user(self):
        """Test that images returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@me.com',
            'testpass'
        )
        Image.objects.create(user=user2,
                             name='MNIST',
                             csvfile=self.csvfile,
                             row=16,
                             label=self.label
                             )
        image = Image.objects.create(user=self.user,
                                     name='MNIST_extended',
                                     csvfile=self.csvfile,
                                     row=0,
                                     label=self.label
                                     )

        res = self.client.get(IMAGES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], image.name)
