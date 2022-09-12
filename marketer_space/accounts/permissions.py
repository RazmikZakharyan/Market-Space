from datetime import timedelta

from rest_framework import permissions
from django.db.models import F

from .models import Account, InviteToken


class IsSuperAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == \
                Account.ACCOUNT_TYPE[0][0]:
            return True
        return False


class IsOrganizationAdmin(permissions.BasePermission):
    organization_admin_methods = ("PUT", "PATCH", "GET", "DELETE")

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == \
                Account.ACCOUNT_TYPE[1][0]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if (
                request.method in self.organization_admin_methods and
                view.kwargs.get(
                    'organization_pk') == request.user.organization_id
        ):
            return True

        return False


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == \
                Account.ACCOUNT_TYPE[2][0]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if (
                request.method == 'GET' and request.user.organization and
                view.kwargs.get('organization_pk') == request.user.organization
        ):
            return True

        return False


class OrganizationAdminHasPermission(IsOrganizationAdmin):

    def has_object_permission(self, request, view, obj):
        if (
                request.data.get(
                    'organization_id') == request.user.organization_id
        ):
            return True

        return False


class InviteTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if InviteToken.objects.filter(
                token=view.kwargs.get('token'),
                used=False,
                created__lt=F('created') + timedelta(days=1)
        ).exists():
            return True
        return False
