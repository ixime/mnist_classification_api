from django.urls import path, include
from rest_framework.routers import DefaultRouter

from dataset import views


router = DefaultRouter()
router.register('csvfiles', views.CsvfileViewSet)
router.register('datasets', views.DatasetViewSet)
router.register('images', views.ImageViewSet)

app_name = 'dataset'

urlpatterns = [
    path('', include(router.urls))
]
