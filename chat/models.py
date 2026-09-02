import uuid
import secrets
from django.db import models
from accounts.models import AnonUser
class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_group = models.BooleanField(default=False)
    name = models.CharField(max_length=100, blank=True)
    participants = models.ManyToManyField(AnonUser, related_name='conversations')
    invite_code = models.CharField(max_length=16, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Conversation {self.id}"

    @staticmethod
    def generate_invite_code():
        return secrets.token_urlsafe(8)


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(AnonUser, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_uploads/%Y/%m/%d/', blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender_id}: {self.text[:30] or self.file_name}"