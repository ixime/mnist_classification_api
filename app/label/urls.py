from django.urls import path, include
from rest_framework.routers import DefaultRouter

from label import views


router = DefaultRouter()
router.register('label', views.LabelViewSet)

app_name = 'label'

urlpatterns = [
    path('', include(router.urls))
]
