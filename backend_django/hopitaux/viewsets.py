from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import RBACPermission

from .models import DeclarationHopitaliere, Hopital
from .serializers import DeclarationHopitaliereSerializer


class DeclarationHopitaliereViewSet(viewsets.ModelViewSet):
    queryset = DeclarationHopitaliere.objects.select_related('hopital', 'mairie').order_by('-created_at')
    serializer_class = DeclarationHopitaliereSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    pagination_class = None
    http_method_names = ['get', 'post', 'head', 'options']

    @property
    def required_permissions(self):
        act = getattr(self, 'action', None)
        if act in ('list', 'retrieve', 'mark_viewed'):
            return ['can_view_hospital_declarations']
        return ['can_create_hospital_declaration']

    def get_queryset(self):
        qs = super().get_queryset()
        role = getattr(self.request.user, 'role', '') or ''

        # Hôpital: uniquement ses déclarations
        if role == 'HOPITAL':
            hopital = Hopital.objects.filter(user=self.request.user).first()
            if not hopital:
                return qs.none()
            return qs.filter(hopital=hopital)

        # Mairie / Officier: voir les déclarations (POC: toutes, à raffiner par rattachement mairie plus tard)
        if role in {'MAIRE', 'OFFICIER_EC'}:
            return qs

        # Autres rôles: rien par défaut
        return qs.none()

    def perform_create(self, serializer):
        hopital = Hopital.objects.filter(user=self.request.user).first()
        if not hopital:
            # pas d'entité hôpital liée à ce user
            raise PermissionDenied("Compte hôpital non configuré.")
        serializer.save(hopital=hopital)

    @action(detail=True, methods=['POST'], url_path='mark-viewed')
    def mark_viewed(self, request, pk=None):
        decl = self.get_object()
        if decl.statut == DeclarationHopitaliere.Statut.ENVOYEE:
            decl.statut = DeclarationHopitaliere.Statut.VUE
            decl.save(update_fields=['statut', 'updated_at'])
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

