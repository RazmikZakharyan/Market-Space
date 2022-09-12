from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from .factories import AccountFactory, OrganizationFactory


class OrganizationListApiViewTest(TestCase):
    def setUp(self):
        self.get_access_tokens()
        self.url = reverse(
            "organizations"
        )

    def get_access_tokens(self):
        url = reverse(
            "token_obtain_pair"
        )
        roles = ['super_admin', 'organization_admin', 'user']
        for role in roles:
            account = AccountFactory(role=role)
            password = account.password
            account.set_password(password)
            account.save()
            setattr(self, role, account)
            access_token = self.client.post(
                url,
                data={
                    "username": account.username,
                    "password": password
                }
            ).json().get('access')

            setattr(self, role + '_token', access_token)

    def test_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(
            self.url,
            {},
            HTTP_AUTHORIZATION=f'JWT {self.super_admin_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            self.url,
            {},
            HTTP_AUTHORIZATION=f'JWT {self.organization_admin_token}'
        )
        self.assertTrue(
            'You do not have permission to perform this action.' ==
            response.data.get('detail')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(
            self.url,
            {},
            HTTP_AUTHORIZATION=f'JWT {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(
            self.url,
            {},
            HTTP_AUTHORIZATION=f'JWT {self.super_admin_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(
            self.url,
            {},
            HTTP_AUTHORIZATION=f'JWT {self.organization_admin_token}'
        )
        self.assertTrue(
            'You do not have permission to perform this action.' ==
            response.data.get('detail')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            self.url,
            {},
            HTTP_AUTHORIZATION=f'JWT {self.user_token}'
        )
        self.assertTrue(
            'You do not have permission to perform this action.' ==
            response.data.get('detail')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrganizationApiViewTest(OrganizationListApiViewTest):
    def setUp(self):
        super().setUp()
        self.organization = OrganizationFactory()

    def test_get_organization_by_id(self):
        self.url = reverse(
            'organization',
            kwargs={'organization_pk': self.organization.id}
        )

        response = self.client.get(
            reverse(
                'organization', kwargs={'organization_pk': 2}
            ),
            {},
            HTTP_AUTHORIZATION=f'JWT {self.organization_admin_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(
            self.url,
            {},
            HTTP_AUTHORIZATION=f'JWT {self.super_admin_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'),
                         self.organization.name)

        response = self.client.get(
            self.url,
            {},
            HTTP_AUTHORIZATION=f'JWT {self.organization_admin_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'),
                         self.organization.name)
