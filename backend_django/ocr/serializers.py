from rest_framework import serializers

from .models import NumerisationOCR


class NumerisationOCRSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumerisationOCR
        fields = [
            'id',
            'image',
            'ocr_text_brut',
            'donnees_extraites',
            'score_confiance',
            'statut',
            'valide_par',
            'acte_cree',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['ocr_text_brut', 'donnees_extraites', 'score_confiance', 'statut', 'valide_par', 'acte_cree', 'created_at', 'updated_at']

