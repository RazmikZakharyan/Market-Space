from django.db import models
from accounts.models import Account


class Campaign(models.Model):
    STATUSES = (
        ('not_started', 'Not Started'),
        ('started', 'Started'),
        ('paused', 'Paused'),
        ('completed', 'Completed')
    )

    uploaded_files = models.ManyToManyField('UploadedFile', blank=True)
    goal = models.TextField()
    campaign_template = models.ForeignKey(
        'CampaignTemplate', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=12, choices=STATUSES, default='not_started'
    )


class CampaignTemplate(models.Model):
    subject = models.CharField(max_length=256)
    content = models.TextField()
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE)


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
