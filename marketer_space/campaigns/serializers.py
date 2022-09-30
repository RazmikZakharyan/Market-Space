import os

from rest_framework import serializers

from .models import Campaign, CampaignTemplate, UploadedFile, Contact


class CampaignCreateSerializers(serializers.ModelSerializer):
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
        if (
                attrs.get('status') and
                attrs.get('status') not in ('not_started', 'started')
        ):
            raise serializers.ValidationError(
                "Status not valid. Choice from list ('not_started', 'started')"
            )
        return attrs


class CampaignUpdateSerializers(serializers.ModelSerializer):
    scheduled_time = serializers.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M']
    )

    class Meta:
        model = Campaign
        fields = (
            'id',
            'goal',
            'campaign_template',
            'scheduled_time',
            'status'
        )
        extra_kwargs = {
            "goal": {"required": False, "allow_null": True},
            "campaign_template": {"required": False, "allow_null": True},
            "id": {'read_only': True}
        }

    def validate(self, attrs):
        if self.instance.status == 'completed':
            raise serializers.ValidationError("Campaign completed.")
        if (
                attrs.get('status') and
                attrs.get('status') in ('paused', 'completed')
        ):
            if self.instance.status == 'not_started':
                raise serializers.ValidationError("Status not valid.")
        if attrs.get('status') == 'started':
            if (not self.instance.campaign_template and
                    not attrs.get('campaign_template')):
                raise serializers.ValidationError(
                    "campaign_template is require when status is starting"
                )

        return attrs


class CampaignTemplateCreateSerializers(serializers.ModelSerializer):
    campaign_id = serializers.IntegerField(write_only=True)

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


class CampaignTemplateUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = CampaignTemplate
        fields = ['id', 'subject', 'content', 'campaign_id']
        extra_kwargs = {
            "id": {'read_only': True}
        }

    def validate(self, attrs):
        if not Campaign.objects.filter(
                id=attrs.get('campaign_id'),
                created_by=self.instance.created_by
        ).exists():
            raise serializers.ValidationError("Campaign not found.")

        return attrs


class UploadedFileSerializers(serializers.ModelSerializer):
    campaign_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UploadedFile
        fields = ['id', 'CSV_file', 'uploaded_by', 'campaign_id']
        extra_kwargs = {
            "id": {'read_only': True}
        }

    def validate(self, attrs):
        if not Campaign.objects.filter(
                id=attrs.get('campaign_id'),
                created_by=attrs.get('uploaded_by')
        ).exists():
            raise serializers.ValidationError(
                {'campaign_id': "Campaign not found."}
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

        return uploaded_file


class ContactSerializers(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
