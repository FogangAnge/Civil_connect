from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from mairies.models import Mairie
from .models import OfficierEC

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.Role.choices)
    nom = serializers.CharField(min_length=2)
    prenom = serializers.CharField(min_length=2)
    telephone = serializers.CharField(required=False, allow_blank=True, default='')
    email = serializers.EmailField(required=False, allow_blank=True)
    nin = serializers.CharField(required=False, allow_blank=True)
    commune = serializers.CharField(required=False, allow_blank=True)
    mairie = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    passwordConfirm = serializers.CharField(write_only=True, min_length=8)
    matricule = serializers.CharField(required=False, allow_blank=True)
    emailOfficiel = serializers.EmailField(required=False, allow_blank=True)
    cleBunec = serializers.CharField(required=False, allow_blank=True)
    codeHabilitation = serializers.CharField(required=False, allow_blank=True)
    codeAdmin = serializers.CharField(required=False, allow_blank=True)
    departement = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        role = attrs['role']
        if attrs['password'] != attrs['passwordConfirm']:
            raise serializers.ValidationError({'passwordConfirm': 'Les mots de passe ne correspondent pas.'})

        if role == User.Role.CITOYEN:
            required = ['email', 'nin', 'commune', 'mairie']
        elif role == User.Role.OFFICIER_EC:
            required = ['emailOfficiel', 'matricule', 'cleBunec', 'mairie']
        elif role == User.Role.ARCHIVISTE:
            required = ['email', 'codeHabilitation', 'mairie']
        elif role == User.Role.ADMIN_BUNEC:
            required = ['email', 'codeAdmin', 'departement']
        else:
            required = ['email']

        errors = {}
        for field in required:
            if not attrs.get(field):
                errors[field] = 'Ce champ est requis.'

        if errors:
            raise serializers.ValidationError(errors)

        if role == User.Role.OFFICIER_EC:
            attrs['email'] = attrs.get('emailOfficiel')

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'Cet email est déjà utilisé.'})

        if role == User.Role.CITOYEN and attrs.get('nin') and User.objects.filter(nin=attrs['nin']).exists():
            raise serializers.ValidationError({'nin': 'Ce numéro CNI est déjà utilisé.'})

        mairie_code = attrs.get('mairie', '').strip()
        if mairie_code:
            mairie = Mairie.objects.filter(code=mairie_code).first()
            if not mairie:
                raise serializers.ValidationError({'mairie': 'Mairie introuvable.'})
            attrs['mairie'] = mairie

        return attrs

    def create(self, validated_data):
        validated_data.pop('passwordConfirm', None)
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        mairie = validated_data.pop('mairie', None)
        email = validated_data.pop('email', '').strip().lower()
        telephone = validated_data.get('telephone', '')
        commune = validated_data.get('commune', '')

        user = User(
            email=email,
            role=role,
            first_name=validated_data.get('prenom', '').strip(),
            last_name=validated_data.get('nom', '').strip(),
            telephone=telephone,
            nin=validated_data.get('nin', '').strip(),
            commune=commune,
            mairie=mairie,
            username=email,
        )
        user.set_password(password)
        user.save()

        if role == User.Role.OFFICIER_EC:
            OfficierEC.objects.create(
                user=user,
                matricule=validated_data.get('matricule', '').strip(),
                cle_certification_bunec=validated_data.get('cleBunec', '').strip(),
            )

        return user
