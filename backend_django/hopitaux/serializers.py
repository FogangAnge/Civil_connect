from rest_framework import serializers

from mairies.models import Mairie

from .models import DeclarationHopitaliere


class DeclarationHopitaliereSerializer(serializers.ModelSerializer):
    mairie_code = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = DeclarationHopitaliere
        fields = [
            'id',
            'hopital',
            'mairie',
            'mairie_code',
            'type_declaration',
            'nom',
            'prenom',
            'date_evenement',
            'lieu',
            'notes',
            'statut',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'hopital', 'mairie', 'statut', 'created_at', 'updated_at']

    def validate(self, attrs):
        # mairie_code → mairie
        code = (attrs.pop('mairie_code', None) or '').strip()
        if not code:
            raise serializers.ValidationError({'mairie_code': 'mairie_code est requis.'})
        mairie = Mairie.objects.filter(code=code).first()
        if not mairie:
            raise serializers.ValidationError({'mairie_code': 'Mairie introuvable pour ce code.'})
        attrs['mairie'] = mairie
        return attrs

