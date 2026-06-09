import uuid

from django.conf import settings
from django.db import models


class NumerisationOCR(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = 'EnAttente', 'En attente'
        VALIDE = 'Valide', 'Validé'
        REJETE = 'Rejete', 'Rejeté'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='ocr_images/')

    ocr_text_brut = models.TextField(blank=True, default='')
    donnees_extraites = models.JSONField(default=dict, blank=True)
    score_confiance = models.FloatField(default=0.0)
    statut = models.CharField(max_length=16, choices=Statut.choices, default=Statut.EN_ATTENTE)

    valide_par = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    acte_cree = models.ForeignKey('acts.ActeNaissance', null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
