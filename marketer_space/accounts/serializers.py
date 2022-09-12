from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from .models import Account, Organization


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'role')


class UserCreateSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Account.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True,
                                     validators=[validate_password])
    repeat_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = (
            'username',
            'password',
            'repeat_password',
            'email',
            'first_name',
            'last_name',
            'country',
            'organization',
            'role'

        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['repeat_password']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('repeat_password')
        password = validated_data.pop('password')
        user = Account.objects.create(**validated_data)

        user.set_password(password)
        user.save()

        return user


class OrganizationSerializers(serializers.ModelSerializer):
    users = UserSerializers(many=True, read_only=True)

    def validate(self, attrs):
        if Organization.objects.filter(
                domain=self.data.get('domain')).exists():
            raise serializers.ValidationError(
                {"message": "Domain exists"})

        return attrs

    class Meta:
        model = Organization
        fields = ('domain', 'name', 'users')


class InviteUserSerializers(serializers.Serializer):
    organization_id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    inviter_role = serializers.ChoiceField(Account.ACCOUNT_TYPE)
    status = serializers.ChoiceField(Account.ACCOUNT_TYPE)

    def validate(self, attrs):
        if not Organization.objects.filter(
                id=attrs['organization_id']).exists():
            raise serializers.ValidationError("Organization not found!")
        if attrs['inviter_role'] == 'organization_admin':
            if attrs['status'] == 'super_admin':
                raise serializers.ValidationError(
                    "You can't invite super user!"
                )
        return attrs
