"""Email backend that reads SMTP settings from SiteSettings."""

from __future__ import annotations

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend


class DatabaseEmailBackend(BaseEmailBackend):
    """Use SMTP credentials from the database; fall back to console when disabled."""

    def _build_connection(self) -> BaseEmailBackend:
        from core.models import SiteSettings

        site = SiteSettings.load()
        if not site.smtp_enabled or not site.smtp_host:
            return ConsoleEmailBackend(fail_silently=self.fail_silently)

        return SMTPEmailBackend(
            host=site.smtp_host,
            port=site.smtp_port or 587,
            username=site.smtp_username or None,
            password=site.smtp_password or None,
            use_tls=site.smtp_use_tls,
            use_ssl=site.smtp_use_ssl,
            fail_silently=self.fail_silently,
            timeout=getattr(settings, "EMAIL_TIMEOUT", None),
        )

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        connection = self._build_connection()
        try:
            return connection.send_messages(email_messages)
        finally:
            connection.close()
