from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Version


def send_email_notifications(version: Version) -> None:
    users = version.project.subscribers.all()

    for user in users:
        message = Mail(
            from_email=settings.NOREPLY_EMAIL_ADDRESS,
            to_emails=user.email,
            subject=f"It's new version of {version.project.title}",
            html_content=f'It\'s new version ({version.title}) of <a href="{version.project.url}">{version.project.title}</a>',
        )
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
