import uuid

from django.conf import settings
from django.db import models

from mairies.models import Mairie


class Hopital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hopital')
    code = models.CharField(max_length=32, unique=True)
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=255, blank=True, default='')
    ville = models.CharField(max_length=120, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.nom} ({self.code})'


class DeclarationHopitaliere(models.Model):
    class TypeDeclaration(models.TextChoices):
        NAISSANCE = 'NAISSANCE', 'Naissance'
        DECES = 'DECES', 'Décès'

    class Statut(models.TextChoices):
        ENVOYEE = 'ENVOYEE', 'Envoyée'
        VUE = 'VUE', 'Vue'
        TRAITEE = 'TRAITEE', 'Traitée'
        REJETEE = 'REJETEE', 'Rejetée'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name='declarations')
    mairie = models.ForeignKey(Mairie, on_delete=models.CASCADE, related_name='declarations_hopital')

    type_declaration = models.CharField(max_length=16, choices=TypeDeclaration.choices)
    # Données minimales (POC) — on pourra enrichir ensuite (parents, etc.)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    date_evenement = models.DateField()
    lieu = models.CharField(max_length=200, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.ENVOYEE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['mairie', 'created_at']),
            models.Index(fields=['hopital', 'created_at']),
            models.Index(fields=['statut']),
        ]

