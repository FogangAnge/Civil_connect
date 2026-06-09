import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=16)  # POST/PUT/PATCH/DELETE
    endpoint = models.CharField(max_length=255)
    ip = models.CharField(max_length=64, blank=True, default='')
    payload_hash = models.CharField(max_length=64, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['endpoint']),
        ]
