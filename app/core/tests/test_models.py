from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='hi@me.com', password='passwrd'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "other@me.com"
        password = "qwert"
        user = sample_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'hi@ME.COM'
        user = sample_user(email=email, password='test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            sample_user(email=None, password='test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'hi@me.com',
            'pswd123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_label_str(self):
        """Test the label string representation"""
        label = models.Label.objects.create(
            user=sample_user(),
            name='shirt'
        )

        self.assertEqual(str(label), label.name)

    def test_csvfile_str(self):
        """Test the csvfile string representation"""
        csvfile = models.Csvfile.objects.create(
            user=sample_user(),
            name='mnist_train.csv',
            labelcol=0,
            imgcolstart=1,
            imgcolend=16
        )

        self.assertEqual(str(csvfile), csvfile.name)

    def test_dataset_str(self):
        """Test the dataset string representation"""
        dataset = models.Dataset.objects.create(
            user=sample_user(),
            name='MNIST'
        )

        self.assertEqual(str(dataset), dataset.name)

#    def test_image_str(self):
#        """Test the image string representation"""
#        image = models.Dataset.objects.create(
#            user=sample_user(),
#            name='001.jpg'
#        )

#        self.assertEqual(str(image), f'{image.csvfile}_{image.id}')

    @patch('uuid.uuid4')
    def test_image_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.dataset_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/dataset/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
