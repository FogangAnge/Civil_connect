from celery import shared_task
from django.core.mail import send_mail


@shared_task
def notify_officier_email(to_email: str, subject: str, message: str) -> None:
    send_mail(subject, message, None, [to_email], fail_silently=True)

