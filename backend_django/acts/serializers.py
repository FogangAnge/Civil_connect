from rest_framework import serializers

from .models import ActeNaissance, DemandeCitoyenne, Parent


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ['id', 'role', 'nom', 'prenom', 'nin', 'statut_mariage']


class ActeNaissanceSerializer(serializers.ModelSerializer):
    parents = ParentSerializer(many=True, required=False)

    class Meta:
        model = ActeNaissance
        fields = [
            'id',
            'numero_acte',
            'nom_enfant',
            'prenom_enfant',
            'date_naissance',
            'lieu_naissance',
            'heure_naissance',
            'sexe',
            'statut',
            'delai_declaration',
            'jugement_requis',
            'ref_jugement',
            'signature_rsa',
            'qr_code_sha256',
            'version',
            'source_acte',
            'mairie',
            'officier',
            'parents',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['delai_declaration', 'jugement_requis', 'numero_acte', 'qr_code_sha256', 'created_at', 'updated_at']

    def create(self, validated_data):
        parents_data = validated_data.pop('parents', [])
        acte = super().create(validated_data)
        for p in parents_data:
            Parent.objects.create(acte=acte, **p)
        return acte


class DemandeCitoyenneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeCitoyenne
        fields = ['id', 'type_demande', 'statut', 'citoyen', 'acte', 'mode_livraison', 'created_at', 'traitee_at']
        read_only_fields = ['created_at', 'traitee_at']

