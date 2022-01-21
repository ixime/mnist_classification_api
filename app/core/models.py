import uuid
import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


def dataset_file_path(instance, filename):
    """Generate file path for new dataset file"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/dataset/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that suppors using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Label(models.Model):
    """Label to be used for a dataset and a model"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Csvfile(models.Model):
    """Csvfile to be used to populate the dataset"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    description = models.TextField(blank=True)
    labelcol = models.IntegerField()
    imgcolstart = models.IntegerField()
    imgcolend = models.IntegerField()
    file = models.FileField(null=True, upload_to=dataset_file_path)

    def __str__(self):
        return self.name


class Dataset(models.Model):
    """Dataset to be used for training a model and prediction"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    description = models.TextField(blank=True)
    labels = models.ManyToManyField(Label)
    csvfiles = models.ManyToManyField(Csvfile)

    def __str__(self):
        return self.name


class Image(models.Model):
    """Image in a dataset"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    csvfile = models.ForeignKey(
        Csvfile,
        on_delete=models.CASCADE
    )
    row = models.IntegerField()
    label = models.ForeignKey(
        Label,
        on_delete=models.CASCADE
    )
    image = models.ImageField(null=True, upload_to=dataset_file_path)
    img_array = models.FileField(null=True, upload_to=dataset_file_path)

    def __str__(self):
        return self.name
