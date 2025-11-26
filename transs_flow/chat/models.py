from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, blank=True)
    is_group = models.BooleanField(default=False)
    participants = models.ManyToManyField(
    settings.AUTH_USER_MODEL, 
    related_name='chat_rooms',
    db_constraint=False   # <-- ADD THIS
)
    updated_at = models.DateTimeField(auto_now=True)

    def display_name_for(self, user):
        if self.is_group:
            return self.name
        else:
            # For private chats, show the other participant's name
            other = self.participants.exclude(id=user.id).first()
            return other.get_full_name() if other else "Private Chat"

    @property
    def display_name(self):
        """Fallback display name if no request.user passed."""
        return self.name or "Chat Room"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    db_constraint=False   # <-- ADD THIS
)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("created_at",)
