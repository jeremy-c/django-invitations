import datetime

from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf import settings
from templated_email import get_templated_mail

from .managers import InvitationManager
from .app_settings import app_settings
from .adapters import get_invitations_adapter
from . import signals


@python_2_unicode_compatible
class Invitation(models.Model):

    email = models.EmailField(unique=True, verbose_name=_('e-mail address'))
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitation', null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    accepted = models.BooleanField(verbose_name=_('accepted'), default=False)
    created = models.DateTimeField(verbose_name=_('created'),
                                   default=timezone.now)
    key = models.CharField(verbose_name=_('key'), max_length=64, unique=True)
    sent = models.DateTimeField(verbose_name=_('sent'), null=True)
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True)

    objects = InvitationManager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.key = get_random_string(64).lower()
        super(Invitation, self).save(force_insert, force_update, using, update_fields)

    @classmethod
    def create(cls, email, group=None, first_name=None, last_name=None, inviter=None):
        key = get_random_string(64).lower()
        instance = cls._default_manager.create(
            email=email,
            group=group,
            first_name=first_name,
            last_name=last_name,
            key=key,
            inviter=inviter)
        return instance

    def key_expired(self):
        expiration_date = (
            self.sent + datetime.timedelta(
                days=app_settings.INVITATION_EXPIRY))
        return expiration_date <= timezone.now()

    def send_invitation(self, request, **kwargs):
        current_site = (kwargs['site'] if 'site' in kwargs
                        else Site.objects.get_current())
        invite_url = reverse('invitations:accept-invite',
                             args=[self.key])
        if request:
            invite_url = request.build_absolute_uri(invite_url)
        else:
            invite_url = 'https://{}{}'.format(current_site.domain, invite_url)

        msg = get_templated_mail(
            template_name='email_invite',
            from_email=self.inviter.email,
            to=[self.email],
            context={
                'invite_url': invite_url,
                'site_name': current_site.name,
                'site_domain': current_site.domain,
                'email': self.email,
                'group': self.group,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'key': self.key,
                'inviter': self.inviter,
            },
            # Optional:
            # cc=['cc@example.com'],
            # bcc=['bcc@example.com'],
            # headers={'My-Custom-Header':'Custom Value'},
            template_dir='invitations/email/',  # Override where the method looks for email templates
            # template_prefix="my_emails/",
            template_suffix="html",
        )

        sender_domain = settings.ANYMAIL['MAILGUN_SENDER_DOMAIN']
        msg.esp_extra = {"sender_domain": sender_domain}

        msg.send()

        self.sent = timezone.now()
        self.save()

        signals.invite_url_sent.send(
            sender=self.__class__,
            instance=self,
            invite_url_sent=invite_url,
            inviter=self.inviter)

    def __str__(self):
        return "Invite: {0}".format(self.email)


# here for backwards compatibility, historic allauth adapter
if hasattr(settings, 'ACCOUNT_ADAPTER'):
    if settings.ACCOUNT_ADAPTER == 'invitations.models.InvitationsAdapter':
        from allauth.account.adapter import DefaultAccountAdapter

        class InvitationsAdapter(DefaultAccountAdapter):

            def is_open_for_signup(self, request):
                if hasattr(request, 'session') and request.session.get(
                        'account_verified_email'):
                    return True
                elif app_settings.INVITATION_ONLY is True:
                    # Site is ONLY open for invites
                    return False
                else:
                    # Site is open to signup
                    return True
