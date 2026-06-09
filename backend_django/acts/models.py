import hashlib
import json
import uuid
from datetime import date

from django.db import models

from mairies.models import Mairie
from users.models import OfficierEC

from .fields import EncryptedCharField


class ActeNaissance(models.Model):
    class Sexe(models.TextChoices):
        M = 'M', 'Masculin'
        F = 'F', 'Féminin'

    class Statut(models.TextChoices):
        ACTIF = 'Actif', 'Actif'
        EN_VALIDATION = 'EnValidation', 'EnValidation'
        EN_CORRECTION = 'EnCorrection', 'EnCorrection'
        ANNULE = 'Annulé', 'Annulé'
        RECTIFIE = 'Rectifié', 'Rectifié'

    class SourceActe(models.TextChoices):
        SAISIE = 'Saisie', 'Saisie'
        OCR = 'OCR', 'OCR'
        SCAN = 'Scan', 'Scan'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_acte = models.CharField(unique=True, max_length=30)

    nom_enfant = models.CharField(max_length=150)
    prenom_enfant = models.CharField(max_length=150)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=200)
    heure_naissance = models.TimeField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=Sexe.choices)

    statut = models.CharField(max_length=16, choices=Statut.choices, default=Statut.EN_VALIDATION)

    delai_declaration = models.IntegerField(default=0)
    jugement_requis = models.BooleanField(default=False)
    ref_jugement = models.CharField(max_length=120, null=True, blank=True)

    signature_rsa = models.TextField(null=True, blank=True)
    qr_code_sha256 = models.CharField(max_length=64, unique=True, null=True, blank=True)

    version = models.IntegerField(default=1)
    source_acte = models.CharField(max_length=8, choices=SourceActe.choices, default=SourceActe.SAISIE)

    mairie = models.ForeignKey(Mairie, on_delete=models.CASCADE)
    officier = models.ForeignKey(OfficierEC, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generer_numero_acte(self) -> str:
        year = self.date_naissance.year
        code = getattr(self.mairie, 'code', '0000')
        # séquence: on compte les actes déjà créés pour l'année+mairie
        seq = (
            ActeNaissance.objects.filter(mairie=self.mairie, date_naissance__year=year)
            .count()
            + 1
        )
        return f'{year}-{code}-N-{seq:05d}'

    def generer_qr_code(self) -> str:
        payload = json.dumps(
            {
                'uuid': str(self.id),
                'numero': self.numero_acte,
                'date': self.date_naissance.isoformat(),
                'mairie': str(self.mairie_id),
            },
            ensure_ascii=False,
            separators=(',', ':'),
        )
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        # délai + jugement requis
        self.delai_declaration = (date.today() - self.date_naissance).days
        self.jugement_requis = self.delai_declaration > 90

        if not self.numero_acte:
            self.numero_acte = self.generer_numero_acte()

        if not self.qr_code_sha256:
            self.qr_code_sha256 = self.generer_qr_code()

        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['nom_enfant']),
            models.Index(fields=['date_naissance']),
            models.Index(fields=['mairie']),
        ]


class Parent(models.Model):
    class Role(models.TextChoices):
        PERE = 'PERE', 'Père'
        MERE = 'MERE', 'Mère'

    class StatutMariage(models.TextChoices):
        MARIE = 'MARIE', 'Marié'
        NON_MARIE = 'NON_MARIE', 'Non marié'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=8, choices=Role.choices)

    # Champs sensibles chiffrés (AES-256)
    nom = EncryptedCharField(max_length=150)
    prenom = EncryptedCharField(max_length=150)
    nin = EncryptedCharField(max_length=64)

    statut_mariage = models.CharField(max_length=12, choices=StatutMariage.choices, default=StatutMariage.NON_MARIE)

    acte = models.ForeignKey(ActeNaissance, on_delete=models.CASCADE, related_name='parents')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DemandeCitoyenne(models.Model):
    class TypeDemande(models.TextChoices):
        COPIE_INTEGRALE = 'COPIE_INTEGRALE', 'Copie intégrale'
        EXTRAIT_SANS_FILIATION = 'EXTRAIT_SANS_FILIATION', 'Extrait sans filiation'

    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        EN_COURS = 'EN_COURS', 'En cours'
        TERMINEE = 'TERMINEE', 'Terminée'
        REJETEE = 'REJETEE', 'Rejetée'

    class ModeLivraison(models.TextChoices):
        TELECHARGEMENT = 'TELECHARGEMENT', 'Téléchargement'
        COURRIER = 'COURRIER', 'Courrier'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_demande = models.CharField(max_length=24, choices=TypeDemande.choices)
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.EN_ATTENTE)

    citoyen = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='demandes')
    acte = models.ForeignKey(ActeNaissance, on_delete=models.CASCADE, related_name='demandes')

    mode_livraison = models.CharField(max_length=16, choices=ModeLivraison.choices, default=ModeLivraison.TELECHARGEMENT)

    created_at = models.DateTimeField(auto_now_add=True)
    traitee_at = models.DateTimeField(null=True, blank=True)
