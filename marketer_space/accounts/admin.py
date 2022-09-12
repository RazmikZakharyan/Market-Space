from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, InviteToken, Organization


@admin.register(Account)
class AccountAdmin(UserAdmin):
    save_as = True
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    save_as = True
    list_display = ["id"]


@admin.register(InviteToken)
class InviteTokenAdmin(admin.ModelAdmin):
    save_as = True


