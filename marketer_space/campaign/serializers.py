from rest_framework import serializers

from .models import Campaign, CampaignTemplate


class CampaignCreateSerializers(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = (
            'goal',
            'scheduled_time',
            'campaign_template',
            'created_by',
            'status'
        )

    def validate(self, attrs):
        if attrs.get('status') not in ('not_started', 'started'):
            raise serializers.ValidationError(
                "Status not valid. Choice from list ('not_started', 'started')"
            )
        return attrs


class CampaignUpdateSerializers(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ('goal', 'campaign_template', 'scheduled_time', 'status')

    def validate(self, attrs):
        if self.instance.status == 'completed':
            raise serializers.ValidationError("Campaign completed.")
        if attrs.get('status') in ('paused', 'completed'):
            if self.instance == 'not_started':
                raise serializers.ValidationError("Status not valid.")


class CampaignTemplateSerializers(serializers.ModelSerializer):
    campaign_id = serializers.IntegerField()

    class Meta:
        model = CampaignTemplate
        fields = ['subject', 'content', 'campaign_id']

    def validate(self, attrs):
        if not Campaign.objects.filter(id=attrs.get('campaign_id')).exists():
            raise serializers.ValidationError("Campaign not found.")

