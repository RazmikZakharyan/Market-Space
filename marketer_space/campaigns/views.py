from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, DestroyAPIView

from .serializers import (
    CampaignSerializers,
    CampaignTemplateSerializers,
    UploadedFileSerializers
)
from .models import Campaign, CampaignTemplate, UploadedFile


class CampaignViewSet(ModelViewSet):
    serializer_class = CampaignSerializers
    permission_classes = [IsAuthenticated]
    queryset = Campaign.objects.all()


class CampaignTemplateViewSet(CampaignViewSet):
    serializer_class = CampaignTemplateSerializers
    permission_classes = [IsAuthenticated]
    queryset = CampaignTemplate.objects.all()


class UploadedFileApiVew(CreateAPIView, DestroyAPIView):
    serializer_class = UploadedFileSerializers
    permission_classes = [IsAuthenticated]
    queryset = UploadedFile.objects.all()
