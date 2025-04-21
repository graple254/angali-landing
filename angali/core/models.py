from django.db import models
from typing import Optional
from django.db import models
from django.utils import timezone

# Create your models here.

# Start of Visitor Tracking Models 👇 ###############################################################################################################

class Visitor(models.Model):
    uuid = models.UUIDField(unique=True, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    visit_date = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return f"Visitor {self.uuid} ({self.ip_address})"


class VisitorSession(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f"Session {self.session_id} of {self.visitor.ip_address}"


class PageInteraction(models.Model):
    session = models.ForeignKey(VisitorSession, on_delete=models.CASCADE)
    section_id = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    scroll_depth = models.PositiveIntegerField(default=0, blank=True, null=True)  # in %

    def __str__(self):
        return f"{self.section_id} @ {self.timestamp}"


# END OF VISITOR TRACKING MODELs 👆 ###############################################################################################################



# START OF WEBSITE OR LANDING PAGE DYNAMIC CONTENT MODELS 👇 ###############################################################################################################

class HeroSection(models.Model):
    """Model representing the hero section of a website."""
    headline = models.CharField(max_length=255, blank=True, null=True)
    subheadline = models.TextField(blank=True, null=True)
    cta_text = models.CharField(
        max_length=100,
        help_text="Text for the call-to-action button",
        blank=True,
        null=True,
    )
    cta_link = models.URLField(
        help_text="URL the button should lead to",
        blank=True,
        null=True,
    )
    background_image = models.ImageField(
        upload_to='hero_images/',
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.headline or "Hero Section"


class SectionContent(models.Model):
    """Model for content sections like About, Mission, etc."""
    SECTION_CHOICES = [
        ('about', 'About'),
        ('how_it_works', 'How It Works'),
        ('mission', 'Our Mission'),
        ('vision', 'Our Vision'),
    ]
    section = models.CharField(
        max_length=50,
        choices=SECTION_CHOICES,
        unique=True,
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='section_images/', blank=True, null=True)

    def __str__(self) -> str:
        return self.title or "Section Content"


class Footer(models.Model):
    """Model for the website footer."""
    platform_name = models.CharField(max_length=100, blank=True, null=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    rights_reserved_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return self.platform_name or "Footer"


class FooterSection(models.Model):
    """Model for sections within the footer."""
    SECTION_CHOICES = [
        ('company', 'Company'),
        ('contact', 'Contact'),
        ('more', 'More'),
        ('community', 'Community/Socials'),
    ]
    footer = models.ForeignKey(
        Footer,
        on_delete=models.CASCADE,
        related_name='sections',
        blank=True,
        null=True,
    )
    title = models.CharField(
        max_length=50,
        choices=SECTION_CHOICES,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.get_title_display() if self.title else "Footer Section"


class FooterLink(models.Model):
    """Model for links within a footer section."""
    section = models.ForeignKey(
        FooterSection,
        on_delete=models.CASCADE,
        related_name='links',
        blank=True,
        null=True,
    )
    label = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return self.label or "Footer Link"


class Testimonial(models.Model):
    """Model for user testimonials."""
    source_name = models.CharField(max_length=100, blank=True, null=True)
    source_handle = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="@handle or link label",
    )
    source_url = models.URLField(
        help_text="Link to the original post",
        blank=True,
        null=True,
    )
    content = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
    )
    show_on_homepage = models.BooleanField(default=True)

    def __str__(self) -> str:
        name = self.source_name or "Anonymous"
        content_preview = (self.content or "")[:40]
        return f"{name} — {content_preview}"


class Partner(models.Model):
    """Model for partner organizations."""
    name = models.CharField(max_length=100, blank=True, null=True)
    logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name or "Partner"


class CallToActionBlock(models.Model):
    """Model for call-to-action blocks."""
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    button_text = models.CharField(max_length=100, blank=True, null=True)
    button_link = models.URLField(blank=True, null=True)
    position = models.CharField(
        max_length=100,
        help_text="e.g., bottom_banner, mid_section",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"CTA: {self.title or 'Untitled'} @ {self.position or 'Unknown'}"


class FAQItem(models.Model):
    """Model for FAQ items."""
    question = models.CharField(max_length=255, blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return self.question or "FAQ Item"


# END OF WEBSITE OR LANDING PAGE DYNAMIC CONTENT MODELS 👆 ###############################################################################################################
