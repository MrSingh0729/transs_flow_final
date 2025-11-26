from django.db import models
from django.conf import settings
from django.utils import timezone

class IssueReport(models.Model):
    SEVERITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Critical", "Critical"),
    ]

    issue_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)

    line_leader = models.CharField(max_length=255)
    operator_id = models.CharField(max_length=100, blank=True, null=True)

    created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,           # ✅ add this
    db_constraint=False
)
    created_at = models.DateTimeField(auto_now_add=True)

    reminder_count = models.IntegerField(default=0)
    last_reminder_at = models.DateTimeField(blank=True, null=True)

    def can_send_reminder(self):
        return self.reminder_count < 3

    def __str__(self):
        return f"{self.issue_name} (#{self.id})"


def issue_image_path(instance, filename):
    return f"issues/{instance.issue.id}/{filename}"


class IssueImage(models.Model):
    issue = models.ForeignKey(IssueReport, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=issue_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)