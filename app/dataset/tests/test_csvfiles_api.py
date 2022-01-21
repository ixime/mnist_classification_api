import tempfile
import os

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Csvfile, Dataset

from dataset.serializers import CsvfileSerializer


CSVFILES_URL = reverse('dataset:csvfile-list')


def file_upload_url(csvfile_id):
    """Return URL for csvfile upload"""
    return reverse('dataset:csvfile-upload-csvfile', args=[csvfile_id])


class PublicCsvfilesApiTests(TestCase):
    """Test the publicly available csvfiles API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(CSVFILES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCsvfilesApiTests(TestCase):
    """Test the private csvfiles API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@me.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_csvfile_list(self):
        """Test retrieving a list of csvfiles"""
        Csvfile.objects.create(user=self.user,
                               name='MNIST_train',
                               labelcol=0,
                               imgcolstart=1,
                               imgcolend=16
                               )

        Csvfile.objects.create(user=self.user,
                               name='MNIST_val',
                               labelcol=0,
                               imgcolstart=1,
                               imgcolend=16
                               )

        res = self.client.get(CSVFILES_URL)

        csvfiles = Csvfile.objects.all().order_by('-name')
        serializer = CsvfileSerializer(csvfiles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_csvfiles_limited_to_user(self):
        """Test that csvfiles for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@me.com',
            'testpass'
        )
        Csvfile.objects.create(user=user2,
                               name='MNIST_train',
                               labelcol=0,
                               imgcolstart=1,
                               imgcolend=16
                               )
        csvfile = Csvfile.objects.create(user=self.user,
                                         name='MNIST_chinese_train',
                                         labelcol=0,
                                         imgcolstart=1,
                                         imgcolend=25
                                         )

        res = self.client.get(CSVFILES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], csvfile.name)

    def test_create_csvfile_successful(self):
        """Test create a new csvfile"""
        payload = {'name': 'MNIST_chinese_train',
                   'labelcol': 0,
                   'imgcolstart': 1,
                   'imgcolend': 25
                   }
        self.client.post(CSVFILES_URL, payload)

        exists = Csvfile.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_csvfile_invalid(self):
        """Test creating invalid csvfile fails"""
        payload = {'name': 'MNIST',
                   'labelcol': 0,
                   'imgcolstart': 1,
                   'imgcolend': ''
                   }
        res = self.client.post(CSVFILES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_csvfiles_assigned_to_datasets(self):
        """Test filtering csvfiles by those assigned to datasets"""
        csvfile1 = Csvfile.objects.create(user=self.user,
                                          name='MNIST_chinese_train',
                                          labelcol=0,
                                          imgcolstart=1,
                                          imgcolend=25
                                          )
        csvfile2 = Csvfile.objects.create(user=self.user,
                                          name='MNIST_chinese_val',
                                          labelcol=0,
                                          imgcolstart=1,
                                          imgcolend=25
                                          )
        dataset = Dataset.objects.create(user=self.user, name='MNIST_chinese')
        dataset.csvfiles.add(csvfile1)

        res = self.client.get(CSVFILES_URL, {'assigned_only': 1})

        serializer1 = CsvfileSerializer(csvfile1)
        serializer2 = CsvfileSerializer(csvfile2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_csvfiles_assigned_unique(self):
        """Test filtering csvfiles by assigned returns unique items"""
        csvfile = Csvfile.objects.create(user=self.user,
                                         name='MNIST_chinese_train',
                                         labelcol=0,
                                         imgcolstart=1,
                                         imgcolend=25
                                         )
        Csvfile.objects.create(user=self.user,
                               name='MNIST_chinese_train',
                               labelcol=0,
                               imgcolstart=1,
                               imgcolend=25
                               )
        dataset1 = Dataset.objects.create(user=self.user, name='MNIST_chinese')
        dataset1.csvfiles.add(csvfile)
        dataset2 = Dataset.objects.create(user=self.user, name='MNIST_zalando')
        dataset2.csvfiles.add(csvfile)

        res = self.client.get(CSVFILES_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)


class CsvfileUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@me.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.csvfile = Csvfile.objects.create(user=self.user,
                                              name='MNIST_chinese_train',
                                              labelcol=0,
                                              imgcolstart=1,
                                              imgcolend=25
                                              )

    def tearDown(self):
        self.csvfile.file.delete()

    def test_upload_file_to_csvfile(self):
        """Test uploading a file to csvfile"""
        url = file_upload_url(self.csvfile.id)
        with tempfile.NamedTemporaryFile(suffix='.csv') as ntf:
            ntf.write(b"label,p0,p1,p2,p3")
            ntf.write(b"cat,0,34,154,29")
            ntf.write(b"dog,0,83,204,93")
            ntf.flush()
            ntf.seek(0)
            res = self.client.post(url, {'file': ntf}, format='multipart')
        self.csvfile.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('file', res.data)
        self.assertTrue(os.path.exists(self.csvfile.file.path))

    def test_upload_file_bad_request(self):
        """Test uploading an invalid file"""
        url = file_upload_url(self.csvfile.id)
        res = self.client.post(url, {'file': 'notfile'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
