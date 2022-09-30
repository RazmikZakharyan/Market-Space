from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, DestroyAPIView

from .serializers import (
    CampaignCreateSerializers,
    CampaignUpdateSerializers,
    CampaignTemplateCreateSerializers,
    CampaignTemplateUpdateSerializers,
    UploadedFileSerializers
)
from .models import Campaign, CampaignTemplate, UploadedFile
from .mixin import UploadFileMixin


class CampaignViewSet(ModelViewSet):
    serializer_class = CampaignCreateSerializers
    permission_classes = [IsAuthenticated]
    queryset = Campaign.objects.all()

    def create(self, request, *args, **kwargs):
        data = self.request.data and self.request.data.dict()
        data['created_by'] = self.request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        self.serializer_class = CampaignUpdateSerializers
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        return Campaign.objects.filter(created_by_id=self.request.user.id)


class CampaignTemplateViewSet(CampaignViewSet):
    serializer_class = CampaignTemplateCreateSerializers
    permission_classes = [IsAuthenticated]
    queryset = CampaignTemplate.objects.all()

    def update(self, request, *args, **kwargs):
        self.serializer_class = CampaignTemplateUpdateSerializers
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        return CampaignTemplate.objects.filter(
            created_by_id=self.request.user.id
        )


class UploadedFileApiVew(UploadFileMixin, CreateAPIView, DestroyAPIView):
    serializer_class = UploadedFileSerializers
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = self.request.data and self.request.data.dict()
        data['uploaded_by'] = self.request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.create_contact(
            serializer.instance.CSV_file.path, serializer.instance.id,
            serializer.instance.uploaded_by.email
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def get_queryset(self):
        return UploadedFile.objects.filter(
            uploaded_by_id=self.request.user.id
        )
