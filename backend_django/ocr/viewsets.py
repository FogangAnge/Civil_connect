from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import RBACPermission, require_permission
from acts.models import ActeNaissance

from .models import NumerisationOCR
from .serializers import NumerisationOCRSerializer
from .tasks import process_ocr_image


class OCRViewSet(viewsets.ModelViewSet):
    queryset = NumerisationOCR.objects.all().order_by('-created_at')
    serializer_class = NumerisationOCRSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permissions = ['can_upload_ocr']

    @action(detail=False, methods=['POST'], url_path='upload')
    def upload(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ocr = ser.save()
        process_ocr_image.delay(str(ocr.id))
        return Response({'id': str(ocr.id), 'status': 'accepted'}, status=202)

    @action(detail=True, methods=['GET'], url_path='result')
    def result(self, request, pk=None):
        ocr = self.get_object()
        return Response(
            {
                'id': str(ocr.id),
                'statut': ocr.statut,
                'score_confiance': ocr.score_confiance,
                'donnees_extraites': ocr.donnees_extraites,
            }
        )

    @action(detail=True, methods=['POST'], url_path='validate')
    @require_permission('can_validate_ocr')
    def validate(self, request, pk=None):
        ocr = self.get_object()
        if ocr.score_confiance < 0.7:
            return Response({'detail': "Score insuffisant: saisie manuelle requise."}, status=400)
        # création acte (minimal)
        data = ocr.donnees_extraites or {}
        acte = ActeNaissance.objects.create(
            numero_acte='',
            nom_enfant=(data.get('nom') or 'INCONNU')[:150],
            prenom_enfant=(data.get('prenoms') or 'INCONNU')[:150],
            date_naissance=request.data.get('date_naissance') or '2026-01-01',
            lieu_naissance=(data.get('lieu') or 'INCONNU')[:200],
            sexe='M',
            mairie_id=request.data.get('mairie'),
            officier_id=request.data.get('officier'),
            source_acte=ActeNaissance.SourceActe.OCR,
        )
        ocr.acte_cree = acte
        ocr.valide_par = request.user
        ocr.statut = NumerisationOCR.Statut.VALIDE
        ocr.save(update_fields=['acte_cree', 'valide_par', 'statut', 'updated_at'])
        return Response({'acte_id': str(acte.id)})

