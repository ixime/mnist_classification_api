from django.test import TestCase
from django.contrib.auth import get_user_model


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
