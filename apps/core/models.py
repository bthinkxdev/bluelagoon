"""Core models: site settings, home page, navigation."""

from __future__ import annotations

from django.db import models

from core.mixins import SEOMixin, SluggedModel, TimeStampedModel


class SiteSettings(models.Model):
    """Singleton site-wide configuration."""

    company_name = models.CharField(max_length=200, default="BLUE LAGOON HOLIDAY CRUISES PVT LTD")
    tagline = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    phone_primary = models.CharField(max_length=30, default="+91 98463 08744")
    phone_secondary = models.CharField(max_length=30, default="+91 9846 30 87 44")
    email = models.EmailField(default="mail@bluelagoonholidays.net")
    address = models.TextField(
        default="AYINI BYPASS LINK ROAD, VITHAYATHIL BUILDING, MARADU, ERNAKULAM, KERALA 682304"
    )
    # Outbound email (SMTP) — configured in Django admin, not .env
    smtp_enabled = models.BooleanField(
        default=False,
        help_text="Enable real SMTP delivery. When off, messages print to the server console.",
    )
    smtp_host = models.CharField(max_length=255, blank=True, help_text="e.g. smtp.gmail.com")
    smtp_port = models.PositiveIntegerField(default=587)
    smtp_use_tls = models.BooleanField(default=True, help_text="Typically on for port 587.")
    smtp_use_ssl = models.BooleanField(
        default=False,
        help_text="Use for port 465 (SSL). Do not enable both TLS and SSL.",
    )
    smtp_username = models.CharField(max_length=255, blank=True)
    smtp_password = models.CharField(max_length=255, blank=True)
    email_from = models.EmailField(
        blank=True,
        help_text="From address on outgoing mail. Defaults to the public contact email.",
    )
    email_notification_to = models.EmailField(
        blank=True,
        help_text="Inbox for contact form submissions. Defaults to the public contact email.",
    )
    email_notification_bcc = models.EmailField(
        blank=True,
        help_text="Optional BCC on staff notification emails.",
    )
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    google_plus_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    copyright_text = models.CharField(max_length=200, default="© Blue Lagoon Holidays")
    google_maps_embed = models.TextField(blank=True, help_text="Google Maps embed URL or API key config")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self) -> str:
        return self.company_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> SiteSettings:
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class OfficeBranch(TimeStampedModel):
    """Contact office branches shown on contact page."""

    name = models.CharField(max_length=120)
    address = models.TextField()
    phone_primary = models.CharField(max_length=30, blank=True)
    phone_secondary = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class NavigationItem(TimeStampedModel):
    """Dynamic navigation menu."""

    label = models.CharField(max_length=80)
    url_name = models.CharField(max_length=120, blank=True, help_text="Django URL name")
    external_url = models.URLField(blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    highlight = models.BooleanField(default=False, help_text="Mark as active section")

    class Meta:
        ordering = ["display_order", "label"]

    def __str__(self) -> str:
        return self.label


class HomeSlider(TimeStampedModel):
    """Homepage revolution slider slides."""

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="sliders/")
    link_url = models.CharField(max_length=255, blank=True)
    link_text = models.CharField(max_length=80, default="View More")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self) -> str:
        return self.title


class HomeFeatureBox(TimeStampedModel):
    """Why you will love section on homepage."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self) -> str:
        return self.title


class HomePackageHighlight(TimeStampedModel):
    """Package category cards on homepage."""

    title = models.CharField(max_length=120)
    description = models.TextField()
    image = models.ImageField(upload_to="home/")
    link_url = models.CharField(max_length=255, blank=True)
    is_external = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self) -> str:
        return self.title


class HomeActivity(TimeStampedModel):
    """Things you may consider section."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="activities/", blank=True, null=True)
    link_url = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self) -> str:
        return self.title


class HomePromoBanner(TimeStampedModel):
    """Sidebar promo banner on homepage."""

    headline = models.CharField(max_length=200)
    highlight_text = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.headline


class HomeSpotlight(TimeStampedModel):
    """Full-width spotlight section (e.g. Wayanad)."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    background_image = models.ImageField(upload_to="spotlight/", blank=True, null=True)
    link_url = models.CharField(max_length=255, blank=True)
    link_text = models.CharField(max_length=80, default="Read more")
    css_class = models.CharField(max_length=80, blank=True, help_text="Extra CSS class e.g. about-wayanad")
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title


class BannerQuerySet(models.QuerySet):
    """Banners visible on the site right now."""

    def active(self) -> BannerQuerySet:
        from django.db.models import Q
        from django.utils import timezone

        now = timezone.now()
        return self.filter(is_active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now),
            Q(end_date__isnull=True) | Q(end_date__gte=now),
        )


class Banner(models.Model):
    """Homepage hero banners (carousel)."""

    ANIMATION_CHOICES = [
        ("fade", "Fade"),
        ("slide", "Slide"),
        ("zoom", "Zoom"),
        ("kenburns", "Ken Burns"),
    ]

    ALIGNMENT_CHOICES = [
        ("left", "Left"),
        ("center", "Center"),
        ("right", "Right"),
    ]

    TEXT_COLOR_CHOICES = [
        ("white", "White"),
        ("dark", "Dark"),
        ("primary", "Primary Blue"),
        ("secondary", "Secondary"),
    ]

    BUTTON_STYLE_CHOICES = [
        ("primary", "Primary"),
        ("outline", "Outline"),
        ("glass", "Glass"),
    ]

    title = models.CharField(max_length=200, help_text="Admin label for this banner")
    subtitle = models.CharField(max_length=255, blank=True, help_text="Small script line above heading")
    heading = models.CharField(
        max_length=255,
        blank=True,
        help_text="Main headline (basic HTML allowed: em, br, strong)",
    )
    description = models.TextField(blank=True)

    desktop_image = models.ImageField(upload_to="banners/")
    mobile_image = models.ImageField(upload_to="banners/mobile/", blank=True, null=True)
    background_video = models.FileField(upload_to="banners/videos/", blank=True, null=True)

    text_alignment = models.CharField(max_length=10, choices=ALIGNMENT_CHOICES, default="left")
    text_color = models.CharField(max_length=20, choices=TEXT_COLOR_CHOICES, default="white")
    overlay_opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.30)

    primary_button_text = models.CharField(max_length=100, blank=True)
    primary_button_url = models.CharField(max_length=255, blank=True)
    primary_button_style = models.CharField(
        max_length=20, choices=BUTTON_STYLE_CHOICES, default="primary"
    )

    secondary_button_text = models.CharField(max_length=100, blank=True)
    secondary_button_url = models.CharField(max_length=255, blank=True)
    secondary_button_style = models.CharField(
        max_length=20, choices=BUTTON_STYLE_CHOICES, default="outline"
    )

    animation = models.CharField(max_length=20, choices=ANIMATION_CHOICES, default="fade")
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BannerQuerySet.as_manager()

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

    def __str__(self) -> str:
        return self.title

    @property
    def hero_image_url(self) -> str:
        return self.desktop_image.url if self.desktop_image else ""

    @property
    def hero_mobile_image_url(self) -> str:
        if self.mobile_image:
            return self.mobile_image.url
        return self.hero_image_url


# Uniform inner-page hero dimensions (see site-pages.css --wl-uniform-hero-*)
PAGE_HERO_WIDTH = 1920
PAGE_HERO_HEIGHT = 400
PAGE_HERO_MOBILE_WIDTH = 390
PAGE_HERO_MOBILE_HEIGHT = 400
PAGE_HERO_MOBILE_BREAKPOINT = 767


class PageHero(TimeStampedModel):
    """One hero banner image per inner page (1920×400 px)."""

    class PageKey(models.TextChoices):
        SERVICES = "services", "Services (/services/)"
        GALLERY = "gallery", "Gallery (/gallery/)"
        PACKAGES_ALL = "packages_all", "All Packages — list (/packages/)"
        PACKAGES_DOMESTIC = (
            "packages_domestic",
            "Domestic Packages — list (/packages/?category=domestic)",
        )
        PACKAGES_INTERNATIONAL = (
            "packages_international",
            "International Packages — list (/packages/?category=international)",
        )
        PACKAGES_PILGRIM = (
            "packages_pilgrim",
            "Pilgrim Packages — list (/packages/?category=pilgrim)",
        )
        ABOUT = "about", "About Us (/about/)"
        CONTACT = "contact", "Contact (/contact/)"
        LANDING_WAYANAD = "landing_wayanad", "Wayanad — landing page (/pages/wayanad/)"
        LANDING_INTERNATIONAL = (
            "landing_international",
            "International — landing page (/pages/international-packages/)",
        )
        LANDING_PILGRIM = (
            "landing_pilgrim",
            "Pilgrim — landing page (/pages/pilgrim-packages/)",
        )

    page_key = models.CharField(
        max_length=40,
        choices=PageKey.choices,
        unique=True,
    )
    image = models.ImageField(
        upload_to="page-heroes/desktop/",
        blank=True,
        help_text=f"Desktop — upload exactly {PAGE_HERO_WIDTH}×{PAGE_HERO_HEIGHT} px.",
    )
    mobile_image = models.ImageField(
        upload_to="page-heroes/mobile/",
        blank=True,
        help_text=(
            f"Mobile — upload exactly {PAGE_HERO_MOBILE_WIDTH}×{PAGE_HERO_MOBILE_HEIGHT} px "
            f"(or {PAGE_HERO_MOBILE_WIDTH * 2}×{PAGE_HERO_MOBILE_HEIGHT * 2} px @2x). "
            "Falls back to the desktop image if empty."
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text="When off, the site uses the built-in placeholder for this page.",
    )

    class Meta:
        ordering = ["page_key"]
        verbose_name = "Page hero"
        verbose_name_plural = "Page heroes"

    def __str__(self) -> str:
        return self.get_page_key_display()

    @property
    def live_path(self) -> str:
        from core.page_heroes import page_hero_live_path

        return page_hero_live_path(self.page_key)
