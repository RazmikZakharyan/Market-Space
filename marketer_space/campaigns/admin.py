from django.contrib import admin
from .models import Campaign, Contact, UploadedFile, CampaignTemplate


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    save_as = True
    list_display = ["id"]
    readonly_fields = ['status']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    save_as = True
    list_display = ["id"]


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    save_as = True
    list_display = ["id"]


@admin.register(CampaignTemplate)
class CampaignTemplateAdmin(admin.ModelAdmin):
    save_as = True
    list_display = ["id"]
