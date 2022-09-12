from django.urls import path
from .views import (
    OrganizationApiView,
    InviteUserApiView,
    InvitedUserApiView,
    OrganizationCreateListApiView
)

urlpatterns = [
    path('organizations/', OrganizationCreateListApiView.as_view(),
         name='organizations'),
    path(
        'organizations/<int:organization_pk>',
        OrganizationApiView.as_view(), name='organization'
    ),
    path('organization/invite/user/', InviteUserApiView.as_view()),
    path(
        'invite/user/token/<slug:token>', InvitedUserApiView.as_view(),
        name='invite_link'
    )
]
