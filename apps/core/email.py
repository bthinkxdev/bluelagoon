"""Helpers for outbound mail using SiteSettings."""

from __future__ import annotations

from core.models import SiteSettings


def get_site_settings() -> SiteSettings:
    return SiteSettings.load()


def get_from_email() -> str:
    site = get_site_settings()
    return site.email_from or site.email


def get_notification_email() -> str:
    site = get_site_settings()
    return site.email_notification_to or site.email


def get_notification_bcc() -> str:
    return get_site_settings().email_notification_bcc or ""
