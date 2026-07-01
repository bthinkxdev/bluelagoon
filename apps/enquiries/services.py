"""Email sending services for enquiries."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from core.email import get_from_email, get_notification_bcc, get_notification_email
from enquiries.models import ContactEnquiry, PackageEnquiry

logger = logging.getLogger("enquiries")


@dataclass
class ContactEmailResult:
    enquiry: ContactEnquiry
    notification_sent: bool
    confirmation_sent: bool


def _get_client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _notification_subject(enquiry: ContactEnquiry) -> str:
    if enquiry.package_id and enquiry.package:
        return f"Package enquiry: {enquiry.package.title} — {enquiry.full_name}"
    return f"Contact form: {enquiry.full_name}"


def _email_context(enquiry: ContactEnquiry) -> dict:
    return {"enquiry": enquiry, "site_name": settings.SITE_NAME}


def send_contact_notification(enquiry: ContactEnquiry) -> bool:
    """Notify staff of a new contact enquiry."""
    to_email = get_notification_email()
    if not to_email:
        logger.error("Contact notification skipped: no notification email configured")
        return False

    subject = _notification_subject(enquiry)
    context = _email_context(enquiry)
    html_body = render_to_string("emails/contact_notification.html", context)
    text_body = render_to_string("emails/contact_notification.txt", context)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=get_from_email(),
            to=[to_email],
            reply_to=[enquiry.email],
        )
        bcc = get_notification_bcc()
        if bcc:
            msg.bcc = [bcc]
        msg.attach_alternative(html_body, "text/html")
        sent = msg.send(fail_silently=False)
        if sent:
            enquiry.email_sent = True
            enquiry.save(update_fields=["email_sent"])
            logger.info("Contact notification sent for enquiry %s to %s", enquiry.pk, to_email)
            return True
        logger.warning("Contact notification returned 0 for enquiry %s", enquiry.pk)
        return False
    except Exception:
        logger.exception("Failed to send contact notification for enquiry %s", enquiry.pk)
        return False


def send_contact_confirmation(enquiry: ContactEnquiry) -> bool:
    """Send confirmation email to the customer."""
    subject = f"Thank you for contacting {settings.SITE_NAME}"
    context = _email_context(enquiry)
    html_body = render_to_string("emails/contact_confirmation.html", context)
    text_body = render_to_string("emails/contact_confirmation.txt", context)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=get_from_email(),
            to=[enquiry.email],
        )
        msg.attach_alternative(html_body, "text/html")
        sent = msg.send(fail_silently=False)
        if sent:
            enquiry.confirmation_sent = True
            enquiry.save(update_fields=["confirmation_sent"])
            logger.info("Contact confirmation sent for enquiry %s", enquiry.pk)
            return True
        logger.warning("Contact confirmation returned 0 for enquiry %s", enquiry.pk)
        return False
    except Exception:
        logger.exception("Failed to send contact confirmation for enquiry %s", enquiry.pk)
        return False


def send_package_enquiry_notification(enquiry: PackageEnquiry) -> bool:
    subject = f"Package enquiry from {enquiry.name}"
    context = {"enquiry": enquiry, "site_name": settings.SITE_NAME}
    html_body = render_to_string("emails/package_enquiry_notification.html", context)
    text_body = render_to_string("emails/package_enquiry_notification.txt", context)

    to_email = get_notification_email()
    if not to_email:
        logger.error("Package enquiry notification skipped: no notification email configured")
        return False

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=get_from_email(),
            to=[to_email],
            reply_to=[enquiry.email],
        )
        bcc = get_notification_bcc()
        if bcc:
            msg.bcc = [bcc]
        msg.attach_alternative(html_body, "text/html")
        sent = msg.send(fail_silently=False)
        if sent:
            enquiry.email_sent = True
            enquiry.save(update_fields=["email_sent"])
            return True
        return False
    except Exception:
        logger.exception("Failed to send package enquiry notification %s", enquiry.pk)
        return False


def save_contact_from_request(form, request) -> ContactEmailResult:
    enquiry = form.save(commit=False)
    enquiry.ip_address = _get_client_ip(request)
    enquiry.save()
    notification_sent = send_contact_notification(enquiry)
    confirmation_sent = send_contact_confirmation(enquiry)
    return ContactEmailResult(
        enquiry=enquiry,
        notification_sent=notification_sent,
        confirmation_sent=confirmation_sent,
    )
