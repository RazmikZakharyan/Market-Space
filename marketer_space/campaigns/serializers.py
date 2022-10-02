import os
import csv

from marketer_space.settings import EMAIL_HOST_USER
from accounts.utils import send_mail

from django_fsm import TransitionNotAllowed, FSMField
from celery import shared_task
from rest_framework import serializers
from django.utils import timezone

from .models import Campaign, CampaignTemplate, UploadedFile, Contact


class CampaignSerializers(serializers.ModelSerializer):
    STATUSES = (
        ('not_start', 'Not Start'),
        ('start', 'Start'),
        ('pause', 'Pause'),
        ('complete', 'Complete')
    )
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    status = serializers.ChoiceField(
        default=STATUSES[0][0],
        choices=STATUSES,
    )

    class Meta:
        model = Campaign
        fields = (
            'id',
            'goal',
            'scheduled_time',
            'campaign_template',
            'created_by',
            'status'
        )
        extra_kwargs = {
            "id": {'read_only': True}
        }

    def validate(self, attrs):
        if attrs.get('status') == 'start':
            if (self.instance and not self.instance.campaign_template and
                    not attrs.get('campaign_template')):
                raise serializers.ValidationError(
                    "campaign_template is require when status is starting"
                )
        return attrs

    def create(self, validated_data):
        state = validated_data.pop('status')
        instance = Campaign(**validated_data)
        self.change_state(instance, state)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        state = validated_data.pop('status')
        self.change_state(instance, state)
        return super().update(instance, validated_data)

    @staticmethod
    def change_state(instance, new_state):
        if new_state:
            try:
                getattr(instance, new_state)()
            except TransitionNotAllowed:
                raise serializers.ValidationError("Invalid transition")


class CampaignTemplateSerializers(serializers.ModelSerializer):
    campaign_id = serializers.IntegerField(write_only=True)
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = CampaignTemplate
        fields = ['id', 'subject', 'content', 'created_by', 'campaign_id']
        extra_kwargs = {
            "id": {'read_only': True}
        }

    def validate(self, attrs):
        if not Campaign.objects.filter(
                id=attrs.get('campaign_id'), created_by=attrs.get('created_by')
        ).exists():
            raise serializers.ValidationError(
                {'campaign_id': "Campaign not found."},
            )

        return attrs

    def create(self, validated_data):
        campaign_id = validated_data.pop('campaign_id')
        campaign_template = CampaignTemplate.objects.create(**validated_data)

        campaign = Campaign.objects.get(id=campaign_id)
        campaign.campaign_template = campaign_template
        campaign.save()

        return campaign_template


class UploadedFileSerializers(serializers.ModelSerializer):
    MAX_UPLOAD_SIZE = 2097152
    campaign_id = serializers.IntegerField(write_only=True)
    uploaded_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UploadedFile
        fields = ['id', 'CSV_file', 'uploaded_by', 'campaign_id']
        extra_kwargs = {
            "id": {'read_only': True}
        }

    def validate(self, attrs):
        campaign = Campaign.objects.filter(
            id=attrs.get('campaign_id'),
            created_by=attrs.get('uploaded_by')
        ).first()

        if not campaign:
            raise serializers.ValidationError(
                {'campaign_id': "Campaign not found."}
            )

        if campaign.status in ['started', 'completed']:
            raise serializers.ValidationError(
                {
                    'campaign_id': "The campaign is started or completed "
                                   "you can't upload files"
                }
            )
        if (
                campaign.status == 'paused' and
                campaign.scheduled_time < timezone.now()
        ):
            raise serializers.ValidationError(
                {
                    'campaign_id': "The scheduled time is hit "
                                   "you can't upload files"
                }
            )

        if attrs.get('CSV_file').size > self.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                {'CSV_file': 'File size is bigger than 2MB'}
            )

        extension = os.path.splitext(
            attrs.get('CSV_file').name
        )[1].replace(".", "")
        if extension.lower() != 'csv':
            raise serializers.ValidationError(
                f'Invalid uploaded file type: {attrs.get("CSV_file")}'
            )

        return attrs

    def create(self, validated_data):
        campaign_id = validated_data.pop('campaign_id')
        uploaded_file = UploadedFile.objects.create(**validated_data)

        campaign = Campaign.objects.get(id=campaign_id)
        campaign.uploaded_files.add(uploaded_file)
        campaign.save()

        # self.create_contacts.delay(
        #     uploaded_file.CSV_file.path, uploaded_file.id,
        #     uploaded_file.uploaded_by.email
        # )
        self.create_contacts(
            uploaded_file.CSV_file.path, uploaded_file.id,
            uploaded_file.uploaded_by.email
        )

        return uploaded_file

    @staticmethod
    # @shared_task
    def create_contacts(csv_path, contact_list, user_email):
        contacts = csv.DictReader(open(csv_path))
        content = "created contact data: \n {} \n " \
                  "not created due to validation: \n {}"
        errors = []
        data = []
        contacts_obj = []
        for row_id, item in enumerate(contacts):
            item['contact_list'] = contact_list
            serializer = ContactSerializers(data=item)
            if serializer.is_valid():
                contacts_obj.append(
                    Contact(**serializer.validated_data)
                )
                data.append(serializer.data)
            else:
                error = serializer.errors
                error['row_id'] = row_id
                errors.append(error)

        Contact.objects.bulk_create(contacts_obj)
        # send_mail(
        #     'Marketer Space',
        #     content.format(data, errors),
        #     EMAIL_HOST_USER,
        #     [user_email]
        # )


class ContactSerializers(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
