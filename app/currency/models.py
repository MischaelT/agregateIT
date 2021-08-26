from currency import model_choices as choices

from django.db import models


class Rate(models.Model):

    ask = models.DecimalField(max_digits=4, decimal_places=2)
    bid = models.DecimalField(max_digits=4, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    bank_name = models.CharField(max_length=16)
    currency_name = models.CharField(max_length=3, choices=choices.RATE_TYPES)


class ContactUs(models.Model):
    email_from = models.EmailField(max_length=32)
    subject = models.CharField(max_length=128)
    message = models.CharField(max_length=2047)
    created = models.DateTimeField(auto_now_add=True)


class Source(models.Model):
    name = models.CharField(max_length=64)
    source_url = models.CharField(max_length=256)


class ResponseLog(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    status_code = models.PositiveSmallIntegerField()
    path = models.CharField(max_length=255)
    response_time = models.PositiveSmallIntegerField(
        help_text='in milliseconds'
    )

# оставшиеся симфолы заменяются пробелами
