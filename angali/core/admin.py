from django.contrib import admin
from django.utils.html import format_html
from django.utils.timesince import timesince
from django.utils import timezone
from .models import *
import datetime

# Inline for VisitorSession to display within Visitor admin
class VisitorSessionInline(admin.TabularInline):
    model = VisitorSession
    extra = 0  # No extra empty forms
    fields = ('session_id', 'start_time', 'duration_seconds', 'referrer', 'user_agent')
    readonly_fields = ('start_time', 'duration_seconds')
    can_delete = True
    show_change_link = True

    def get_queryset(self, request):
        # Optimize query by selecting related visitor
        return super().get_queryset(request).select_related('visitor')

# Inline for PageInteraction to display within VisitorSession admin
class PageInteractionInline(admin.TabularInline):
    model = PageInteraction
    extra = 0
    fields = ('section_id', 'timestamp', 'scroll_depth')
    readonly_fields = ('timestamp',)
    can_delete = True

    def get_queryset(self, request):
        # Optimize query by selecting related session
        return super().get_queryset(request).select_related('session')

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'ip_address', 'location', 'formatted_visit_date', 'session_count')
    list_filter = ('visit_date', 'location')
    search_fields = ('uuid__exact', 'ip_address', 'location')
    inlines = [VisitorSessionInline]
    readonly_fields = ('uuid', 'visit_date')
    list_per_page = 25
    date_hierarchy = 'visit_date'

    def formatted_visit_date(self, obj):
        """Display visit date in a human-readable format."""
        return timesince(obj.visit_date) + " ago"
    formatted_visit_date.short_description = 'Visited'
    formatted_visit_date.admin_order_field = 'visit_date'

    def session_count(self, obj):
        """Display the number of sessions for this visitor."""
        count = obj.visitorsession_set.count()
        return format_html('<b style="color: {};">{}</b>', 'green' if count > 0 else 'red', count)
    session_count.short_description = 'Sessions'
    session_count.admin_order_field = 'visitorsession__count'

    def get_queryset(self, request):
        # Optimize query by prefetching related sessions
        return super().get_queryset(request).prefetch_related('visitorsession_set')

@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'visitor_ip', 'start_time', 'formatted_duration', 'referrer_short', 'user_agent_short', 'interaction_count')
    list_filter = ('start_time', 'visitor__location')
    search_fields = ('session_id', 'visitor__ip_address', 'referrer', 'user_agent')
    inlines = [PageInteractionInline]
    readonly_fields = ('start_time', 'duration_seconds')
    list_per_page = 25
    date_hierarchy = 'start_time'
    actions = ['reset_duration']

    def visitor_ip(self, obj):
        """Display the visitor's IP address."""
        return obj.visitor.ip_address
    visitor_ip.short_description = 'Visitor IP'
    visitor_ip.admin_order_field = 'visitor__ip_address'

    def formatted_duration(self, obj):
        """Display duration in a colored format based on length."""
        seconds = obj.duration_seconds or 0
        color = 'green' if seconds < 300 else 'orange' if seconds < 600 else 'red'
        return format_html('<span style="color: {};">{}s</span>', color, seconds)
    formatted_duration.short_description = 'Duration'
    formatted_duration.admin_order_field = 'duration_seconds'

    def referrer_short(self, obj):
        """Truncate referrer URL for display."""
        return obj.referrer[:50] + ('...' if len(obj.referrer or '') > 50 else '')
    referrer_short.short_description = 'Referrer'
    referrer_short.admin_order_field = 'referrer'

    def user_agent_short(self, obj):
        """Truncate user agent for display."""
        return obj.user_agent[:50] + ('...' if len(obj.user_agent or '') > 50 else '')
    user_agent_short.short_description = 'User Agent'
    user_agent_short.admin_order_field = 'user_agent'

    def interaction_count(self, obj):
        """Display the number of page interactions."""
        count = obj.pageinteraction_set.count()
        return format_html('<b>{}</b>', count)
    interaction_count.short_description = 'Interactions'
    interaction_count.admin_order_field = 'pageinteraction__count'

    def reset_duration(self, request, queryset):
        """Admin action to reset duration_seconds to 0."""
        updated = queryset.update(duration_seconds=0)
        self.message_user(request, f"Reset duration for {updated} session(s).")
    reset_duration.short_description = "Reset session duration to 0"

    def get_queryset(self, request):
        # Optimize query by selecting related visitor and prefetching interactions
        return super().get_queryset(request).select_related('visitor').prefetch_related('pageinteraction_set')

@admin.register(PageInteraction)
class PageInteractionAdmin(admin.ModelAdmin):
    list_display = ('section_id', 'session_id_short', 'timestamp', 'scroll_depth_percent')
    list_filter = ('timestamp', 'section_id')
    search_fields = ('section_id', 'session__session_id')
    readonly_fields = ('timestamp',)
    list_per_page = 25
    date_hierarchy = 'timestamp'

    def session_id_short(self, obj):
        """Display a shortened session ID."""
        return obj.session.session_id[:20] + ('...' if len(obj.session.session_id or '') > 20 else '')
    session_id_short.short_description = 'Session ID'
    session_id_short.admin_order_field = 'session__session_id'

    def scroll_depth_percent(self, obj):
        """Display scroll depth with a percentage sign."""
        return f"{obj.scroll_depth or 0}%"
    scroll_depth_percent.short_description = 'Scroll Depth'
    scroll_depth_percent.admin_order_field = 'scroll_depth'

    def get_queryset(self, request):
        # Optimize query by selecting related session and visitor
        return super().get_queryset(request).select_related('session__visitor')
    

# Start of Website or Landing Page Dynamic Content Models Admins 👇 ###############################################################################################################
    

# --- Inlines ---

class FooterSectionInline(admin.TabularInline):
    model = FooterSection
    extra = 1
    show_change_link = True

class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1

class FooterLinkInlineForSection(admin.TabularInline):
    model = FooterLink
    extra = 1
    fk_name = 'section'

# --- Admins ---

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ('headline', 'cta_text', 'is_active', 'background_image_preview')
    list_filter = ('is_active',)
    search_fields = ('headline', 'subheadline', 'cta_text')
    readonly_fields = ('background_image_preview',)
    fieldsets = (
        (None, {
            'fields': ('headline', 'subheadline', 'cta_text', 'cta_link', 'is_active')
        }),
        ('Background', {
            'fields': ('background_image', 'background_image_preview')
        }),
    )

    def background_image_preview(self, obj):
        if obj.background_image:
            return format_html('<img src="{}" style="max-height:80px; max-width:200px;" />', obj.background_image.url)
        return "-"
    background_image_preview.short_description = "Background Preview"

@admin.register(SectionContent)
class SectionContentAdmin(admin.ModelAdmin):
    list_display = ('section', 'title', 'image_preview', 'short_content')
    list_filter = ('section',)
    search_fields = ('title', 'content')
    readonly_fields = ('image_preview',)
    fieldsets = (
        (None, {
            'fields': ('section', 'title', 'content')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:60px; max-width:120px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image Preview"

    def short_content(self, obj):
        if obj.content:
            return obj.content[:40] + ("..." if len(obj.content) > 40 else "")
        return ""
    short_content.short_description = "Content Preview"

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('platform_name', 'tagline', 'rights_reserved_text')
    search_fields = ('platform_name', 'tagline')
    inlines = [FooterSectionInline]

@admin.register(FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'footer')
    list_filter = ('title',)
    search_fields = ('footer__platform_name',)
    inlines = [FooterLinkInlineForSection]

@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'section', 'order')
    list_filter = ('section',)
    search_fields = ('label', 'url')
    ordering = ('section', 'order')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('source_name', 'source_handle', 'short_content', 'show_on_homepage', 'profile_image_preview')
    list_filter = ('show_on_homepage',)
    search_fields = ('source_name', 'source_handle', 'content')
    readonly_fields = ('profile_image_preview',)
    fieldsets = (
        (None, {
            'fields': ('source_name', 'source_handle', 'source_url', 'content', 'show_on_homepage')
        }),
        ('Profile Image', {
            'fields': ('profile_image', 'profile_image_preview')
        }),
    )

    def short_content(self, obj):
        if obj.content:
            return obj.content[:40] + ("..." if len(obj.content) > 40 else "")
        return ""
    short_content.short_description = "Testimonial"

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="max-height:50px; max-width:50px; border-radius:50%;" />', obj.profile_image.url)
        return "-"
    profile_image_preview.short_description = "Profile Image"

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'logo_preview')
    search_fields = ('name',)
    readonly_fields = ('logo_preview',)
    fieldsets = (
        (None, {
            'fields': ('name', 'website')
        }),
        ('Logo', {
            'fields': ('logo', 'logo_preview')
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height:40px; max-width:100px;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = "Logo"

@admin.register(CallToActionBlock)
class CallToActionBlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'button_text', 'position', 'is_active')
    list_filter = ('is_active', 'position')
    search_fields = ('title', 'description', 'button_text', 'position')

@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'short_answer', 'order')
    search_fields = ('question', 'answer')
    ordering = ('order',)

    def short_answer(self, obj):
        if obj.answer:
            return obj.answer[:50] + ("..." if len(obj.answer) > 50 else "")
        return ""
    short_answer.short_description = "Answer"
