from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    CampaignCreateSerializers,
    CampaignUpdateSerializers,
    CampaignTemplateSerializers
)
from .models import Campaign


class CampaignApiView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    serializer_class = CampaignCreateSerializers
    permission_classes = IsAuthenticated
    lookup_field = 'campaign_pk'

    def create(self, request, *args, **kwargs):
        data = request.data.dict()
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


class CampaignTemplateApiView():
    pass
