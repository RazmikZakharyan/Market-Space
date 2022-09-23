from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    ACCOUNT_TYPE = (
        ('super_admin', 'Super Admin'),
        ('organization_admin', 'Organization Admin'),
        ('user', 'User')
    )

    country = models.CharField(max_length=128)
    organization = models.ForeignKey(
        "Organization", on_delete=models.CASCADE, null=True,
        related_name='users'
    )

    profile_picture = models.ImageField(upload_to='profile/%Y/%m')
    role = models.CharField(
        max_length=45,
        choices=ACCOUNT_TYPE,
    )

    creation_date = models.DateTimeField(auto_now=True, null=True)
    modification_date = models.DateTimeField(null=True)


class InviteToken(models.Model):
    token = models.CharField(max_length=256, unique=True)
    status = models.CharField(max_length=20, choices=Account.ACCOUNT_TYPE)
    used = models.BooleanField(default=False)
    organization = models.ForeignKey(
        "Organization", on_delete=models.CASCADE, null=True
    )
    created = models.DateTimeField(auto_now_add=True)


class Organization(models.Model):
    domain = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=128)


class Campaign(models.Model):
    STATUSES = (
        'not_started', 'started', 'paused', 'completed'
    )

    uploaded_files = models.ManyToManyField('UploadedFile')
    goal = models.TextField()
    scheduled_time = models.DateTimeField()
    status = models.CharField(choices=STATUSES)


class UploadedFile(models.Model):
    CSV_file = models.FileField(upload_to='uploaded_files/%Y/%m')
    uploaded_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(Account, on_delete=models.CASCADE)


class Contact(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField()
    company_name = models.CharField(max_length=256)
    job_title = models.CharField(max_length=256)
    contact_list = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)


