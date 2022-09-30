from marketer_space.settings import EMAIL_HOST_USER
from rest_framework import status
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
)
from rest_framework.response import Response

from .permissions import (
    IsUser,
    OrganizationAdminHasPermission,
    IsOrganizationAdmin,
    IsSuperAdmin,
    InviteTokenPermission
)
from .models import InviteToken
from .utils import send_email
from .serializers import (
    OrganizationSerializers, InviteUserSerializers, UserCreateSerializers
)
from .mixin import TokenMixin
from .models import Organization


class InvitedUserApiView(CreateAPIView):
    serializer_class = UserCreateSerializers
    permission_classes = [InviteTokenPermission]

    def create(self, request, *args, **kwargs):
        invite_token = InviteToken.objects.get(token=self.kwargs.get('token'))
        data = self.request.data and self.request.data.dict()
        data.update(
            {
                'organization': invite_token.organization_id,
                'role': invite_token.status,
            }
        )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        invite_token.used = True
        invite_token.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class OrganizationCreateListApiView(CreateAPIView, ListAPIView):
    serializer_class = OrganizationSerializers
    permission_classes = [IsSuperAdmin]
    queryset = Organization.objects.all()


class OrganizationApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializers
    permission_classes = [
        IsSuperAdmin | IsOrganizationAdmin | IsUser
    ]
    queryset = Organization.objects.all()
    lookup_url_kwarg = 'organization_pk'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        if self.request.user.role == 'user':
            data.pop('users')

        return Response(data)


class InviteUserApiView(CreateAPIView, TokenMixin):
    serializer_class = InviteUserSerializers
    permission_classes = [IsSuperAdmin | OrganizationAdminHasPermission]

    def create(self, request, *args, **kwargs):
        data = self.request.data and self.request.data.dict()
        data['inviter_role'] = self.request.user.role

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)

        message = '{} {} ({}) has invited you to join {} organization: \n' \
                  ' Accept [{}]'
        subject = 'Invitation from {} {}: Marketer Space'.format(
            self.request.user.first_name,
            self.request.user.last_name
        )

        send_email(
            subject,
            message.format(
                serializer.data['first_name'],
                serializer.data['last_name'],
                serializer.data['email'],
                Organization.objects.only('name').get(
                    id=serializer.data['organization_id']
                ).name,
                self.create_invite_link(serializer.data)
            ),
            EMAIL_HOST_USER,
            [serializer.data.get('email')]
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)
