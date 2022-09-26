from django.urls import path, include
from rest_framework import routers
from .views import (
    CampaignViewSet, CampaignTemplateViewSet, UploadedFileApiVew
)

router = routers.DefaultRouter()
router.register('templates', CampaignTemplateViewSet)
router.register('', CampaignViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('uploadfile', UploadedFileApiVew.as_view()),
    path('uploadfile/<int:pk>', UploadedFileApiVew.as_view()),
]
