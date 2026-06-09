import json

from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.permissions import RBACPermission, require_permission

from .models import ActeNaissance, DemandeCitoyenne
from .serializers import ActeNaissanceSerializer, DemandeCitoyenneSerializer
from .services.crypto import RSAService, generate_qr_code
from .tasks import notify_officier_email


class BirthActViewSet(viewsets.ModelViewSet):
    queryset = ActeNaissance.objects.all().order_by('-created_at')
    serializer_class = ActeNaissanceSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permissions = ['can_create_act']

    def create(self, request, *args, **kwargs):
        data = request.data
        # anti-doublon: nom+prenom+date+mairie
        if ActeNaissance.objects.filter(
            nom_enfant=data.get('nom_enfant'),
            prenom_enfant=data.get('prenom_enfant'),
            date_naissance=data.get('date_naissance'),
            mairie_id=data.get('mairie'),
        ).exists():
            raise ValidationError("Doublon détecté: un acte similaire existe déjà pour cette mairie.")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        acte = serializer.save()

        # audit: le middleware capture déjà, ici on peut compléter plus tard
        try:
            to_email = getattr(getattr(acte.officier, 'user', None), 'email', None)
            if to_email:
                notify_officier_email.delay(
                    to_email,
                    "CivilConnect — Acte en validation",
                    f"L'acte {acte.numero_acte} a été créé et attend validation.",
                )
        except Exception:
            pass

        out = self.get_serializer(acte).data
        return Response(out, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'], url_path='sign')
    @require_permission('can_sign_act')
    def sign_act(self, request, pk=None):
        acte = self.get_object()
        private_pem = request.data.get('private_pem') or ''
        if not private_pem:
            raise ValidationError("private_pem requis pour signer (mock).")
        payload = json.dumps(
            {'uuid': str(acte.id), 'numero': acte.numero_acte, 'version': acte.version},
            separators=(',', ':'),
            ensure_ascii=False,
        )
        acte.signature_rsa = RSAService.sign_data(private_pem, payload)
        acte.statut = ActeNaissance.Statut.ACTIF
        acte.save(update_fields=['signature_rsa', 'statut', 'updated_at'])
        return Response({'status': 'signed'})

    @action(detail=True, methods=['GET'], url_path='qr')
    def generate_qr(self, request, pk=None):
        acte = self.get_object()
        sha256_hash, image_path = generate_qr_code(
            str(acte.id),
            acte.numero_acte,
            acte.date_naissance.isoformat(),
            str(acte.mairie_id),
        )
        if acte.qr_code_sha256 != sha256_hash:
            acte.qr_code_sha256 = sha256_hash
            acte.save(update_fields=['qr_code_sha256', 'updated_at'])
        return FileResponse(open(image_path, 'rb'), content_type='image/png')

    @action(detail=False, methods=['GET'], url_path='verify/(?P<qr_hash>[^/.]+)', permission_classes=[AllowAny])
    def verify_qr(self, request, qr_hash=None):
        acte = ActeNaissance.objects.filter(qr_code_sha256=qr_hash).select_related('mairie', 'officier').first()
        if not acte:
            return Response({'valid': False, 'message': 'Acte invalide.'}, status=404)
        return Response(
            {
                'valid': True,
                'nom': acte.nom_enfant,
                'date': acte.date_naissance.isoformat(),
                'mairie': acte.mairie.nom,
                'officier': getattr(acte.officier, 'matricule', ''),
                'statut': 'VALIDE',
            }
        )


class DemandeViewSet(viewsets.ModelViewSet):
    queryset = DemandeCitoyenne.objects.all().order_by('-created_at')
    serializer_class = DemandeCitoyenneSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permissions = ['can_create_demand']

    def perform_create(self, serializer):
        serializer.save(citoyen=self.request.user)

