from django.db import models
from django_fsm import FSMField, transition

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
    status = FSMField(default=STATUSES[0][0], choices=STATUSES, protected=True)

    @transition(field=status, source=['not_started', 'started', 'paused'],
                target='not_started')
    def not_start(self):
        return 'not_started'

    @transition(field=status, source=['not_started', 'paused'],
                target='started')
    def start(self):
        return 'started'

    @transition(field=status, source=['started'], target='paused')
    def pause(self):
        return 'pause'

    @transition(field=status, source=['started', 'paused'], target='completed')
    def complete(self):
        return 'complete'


class CampaignTemplate(models.Model):
    subject = models.CharField(max_length=256)
    content = models.TextField()
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE)


class UploadedFile(models.Model):
    CSV_file = models.FileField(upload_to='uploaded_files/%Y/%m')
    uploaded_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True
    )


class Contact(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    mail = models.EmailField()
    company_name = models.CharField(max_length=256)
    job_title = models.CharField(max_length=256)
    contact_list = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
