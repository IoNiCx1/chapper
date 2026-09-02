import uuid
import secrets
from django.db import models


class AnonUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_token = models.CharField(max_length=64, unique=True, db_index=True)
    display_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or str(self.id)

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)
    @property
    def is_authenticated(self):
        return True

    

    