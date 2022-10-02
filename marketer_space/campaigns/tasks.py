from string import Formatter

from celery import shared_task

from django.utils import timezone

from marketer_space.settings import EMAIL_HOST_USER

from accounts.utils import send_mail
from campaigns.models import Campaign, Contact


@shared_task
def campaign_task():
    if not Campaign.objects.filter(
            status='started', scheduled_time__lte=timezone.now()
    ).exists():
        return None

    campaigns = Campaign.objects.filter(
        status='started', scheduled_time__lte=timezone.now()
    ).select_related('campaign_template')
    for campaign in campaigns:
        contacts = Contact.objects.filter(
            contact_list_id__in=campaign.uploaded_files.only('id').all())
        for contact in contacts:
            content = campaign.campaign_template.content
            args = [
                arg[1] for arg in Formatter().parse(content) if
                arg[1] is not None
            ]
            print(
                content.format(
                    **{item: getattr(contact, item) for item in args}
                )
            )
            # send_mail(
            #     campaign.campaign_template.subject,
            #     campaign.campaign_template.content.format(contact.first_name),
            #     EMAIL_HOST_USER,
            #     [contact.mail]
            # )
        campaign.complete()
        campaign.save()
