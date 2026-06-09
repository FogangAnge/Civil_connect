from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CITOYEN = 'CITOYEN', 'Citoyen'
        OFFICIER_EC = 'OFFICIER_EC', 'Officier EC'
        ARCHIVISTE = 'ARCHIVISTE', 'Archiviste'
        ADMIN_BUNEC = 'ADMIN_BUNEC', 'Admin BUNEC'
        MAIRE = 'MAIRE', 'Maire'
        RESP_SEC = 'RESP_SEC', 'Responsable Sécurité'
        HOPITAL = 'HOPITAL', 'Hôpital'

    username = models.CharField(max_length=150, unique=False, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.CITOYEN)
    telephone = models.CharField(max_length=32, blank=True, default='')

    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class OfficierEC(models.Model):
    import uuid

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='officier_ec')
    matricule = models.CharField(max_length=64, unique=True)
    cle_certification_bunec = models.CharField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'OfficierEC({self.matricule})'
