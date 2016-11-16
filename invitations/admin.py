from django.contrib import admin

from .models import Invitation
from .forms import InvitationAdminAddForm, InvitationAdminChangeForm
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib.auth.models import Group
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget
from django.conf import settings
from django.utils.crypto import get_random_string



class InvitationResource(resources.ModelResource):
    group = fields.Field(
        column_name='group',
        attribute='group',
        widget=ForeignKeyWidget(Group, 'name'))
    # inviter = fields.Field(
    #     column_name='inviter',
    #     attribute='inviter',
    #     widget=ForeignKeyWidget(settings.AUTH_USER_MODEL, 'email'))

    class Meta:
        model = Invitation

    def after_save_instance(self, instance, using_transactions, dry_run):
        if not dry_run:
            instance.key = get_random_string(64).lower()
            instance.send_invitation(None)


class InvitationAdmin(ImportExportModelAdmin):
    resource_class = InvitationResource
    list_display = ('email', 'first_name', 'last_name', 'group', 'sent', 'accepted')

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = InvitationAdminChangeForm
        else:
            kwargs['form'] = InvitationAdminAddForm
            kwargs['form'].user = request.user
            kwargs['form'].request = request
        return super(InvitationAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(Invitation, InvitationAdmin)
