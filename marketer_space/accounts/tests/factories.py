import factory
from django.contrib.auth.hashers import make_password

from accounts.models import Organization, Account


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Faker('name')


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account
        django_get_or_create = ["role"]

    username = factory.Faker('email')
    password = factory.Faker('password')

    is_active = True
