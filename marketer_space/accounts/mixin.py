import secrets

from django.contrib.sites.shortcuts import get_current_site
from rest_framework.reverse import reverse

from .models import InviteToken


class TokenMixin:
    @staticmethod
    def generate_token():
        token = secrets.token_hex()
        return not InviteToken.objects.filter(
            token=token).exists() and token or TokenMixin.generate_token()

    def create_invite_link(self, serializer_data):
        token = InviteToken.objects.create(
            token=self.generate_token(),
            status=serializer_data.get('status'),
            organization_id=serializer_data.get('organization_id')
        ).token

        link = reverse(
            'invite_link',
            kwargs={
                'token': token
            }
        )
        domain = get_current_site(self.request).domain
        scheme = self.request.is_secure() and "https" or "http"

        return f'{scheme}://{domain}{link}'
