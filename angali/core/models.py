from django.db import models
from django.utils import timezone
# Create your models here.

# Visitor model tracks new visitors to our site.  👇 ###############################################################################################################

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
