import logging
from threading import Thread

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send(subject, message, recipients):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
    except Exception:
        logger.exception("ProjectNest email delivery failed")


def send_email_async(subject, message, recipients):
    Thread(target=_send, args=(subject, message, recipients), daemon=True).start()
