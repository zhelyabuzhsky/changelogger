from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from changelogs.models import Version
from changelogs.services import send_email_notifications


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Version)
def send_notifications(sender, instance=None, created=False, **kwargs):
    if created and not settings.DEBUG and settings.SENDGRID_API_KEY:
        send_email_notifications(version=instance)
