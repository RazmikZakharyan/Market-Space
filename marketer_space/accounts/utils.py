import smtplib

from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response


def send_mail(subject, message, from_email, recipient_list):
    try:
        send_mail(
            subject=subject,
            from_email=from_email,
            message=message,
            recipient_list=recipient_list,
        )
    except smtplib.SMTPException:

        return Response(
            {'message': 'Error for SMTP misconfiguration - Having trouble'
                        ' sending an activation email. Please, contact to'
                        ' our support.'},
            status=status.HTTP_400_BAD_REQUEST
        )