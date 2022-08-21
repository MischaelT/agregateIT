import asyncio

from celery import shared_task

from django.core.mail import send_mail

from settings import settings

from currency.parsers import make_tasks


@shared_task
def send_email(subject, full_email, recipient_list):

    """
        Celery task for sending email

        subject(str): subject of message
        full_email(str): full text of email
        recipient_list(list): list of recipients
    """

    recipient_list.append(settings.SUPPORT_EMAIL)

    send_mail(
        subject,
        full_email,
        settings.EMAIL_HOST,
        recipient_list,
        fail_silently=False,
    )


@shared_task
def run_parsing():
    tasks = make_tasks()
    asyncio.run(asyncio.gather(*tasks, return_exceptions=True))
