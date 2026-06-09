import uuid

from django.db import models


class Mairie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=16, unique=True)
    nom = models.CharField(max_length=200)
    region = models.CharField(max_length=120)
    departement = models.CharField(max_length=120, blank=True, default='')
    commune = models.CharField(max_length=120, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['region']),
            models.Index(fields=['code']),
        ]

    def __str__(self) -> str:
        return f'{self.nom} ({self.code})'
