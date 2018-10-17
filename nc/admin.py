# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.account.adapter import get_adapter

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as auth_UserAdmin
from django.contrib.sites.shortcuts import get_current_site

from . import models

# Register your models here.
admin.site.register(models.Profile)
admin.site.register(models.Account)
admin.site.register(models.AccountFundRequest)
admin.site.register(models.Activity)
admin.site.register(models.Asset)
admin.site.register(models.Comment)
admin.site.register(models.Portfolio)
admin.site.register(models.RawPortfolioData)

# Override auth user admin to allow for bulk user email sendouts
# NOTE: Need to unregister first before registering again with the override.
class UserAdmin(auth_UserAdmin):
    """
    Override to include function for bulk email of
    templates.
    """
    actions = ['email_feedback_form']

    def email_feedback_form(self, request, queryset):
        # Send individual emails to all users in queryset
        current_site = get_current_site(request)
        recipient_context_list = [
            (u.email, {'current_site': current_site, 'username': u.username})
            for u in queryset
        ]
        get_adapter(request).send_bulk_mail('nc/email/feedback_form', recipient_context_list)

        users_sent_emails = len(recipient_context_list)
        if users_sent_emails == 1:
            message_bit = "1 user was"
        else:
            message_bit = "%s users were" % users_sent_emails
        self.message_user(request, "%s successfully emailed." % message_bit)
    email_feedback_form.short_description = "Email feedback form to selected users"

user_model = get_user_model()
admin.site.unregister(user_model)
admin.site.register(user_model, UserAdmin)
