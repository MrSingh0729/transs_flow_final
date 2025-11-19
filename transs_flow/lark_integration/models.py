from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL


class LarkProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lark_profile')
    open_id = models.CharField(max_length=255, unique=True)
    union_id = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    extra = models.JSONField(default=dict, blank=True)


    def __str__(self):
        return f"LarkProfile({self.name})"