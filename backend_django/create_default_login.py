"""
Crée des comptes de démo pour se connecter (à supprimer en production).
Usage:  set DJANGO_USE_SQLITE=1   (ou configurer Postgres)
        py create_default_login.py
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from mairies.models import Mairie  # noqa: E402
from users.models import OfficierEC  # noqa: E402

User = get_user_model()

DEFAULT_PASSWORD = "Civil123!"


def upsert_user(email: str, role: str, **extra):
    u, _ = User.objects.get_or_create(email=email, defaults={"role": role, **extra})
    u.role = role
    for k, v in extra.items():
        setattr(u, k, v)
    u.set_password(DEFAULT_PASSWORD)
    u.save()
    return u


def main():
    upsert_user(
        "citoyen@civilconnect.cm",
        User.Role.CITOYEN,
        telephone="+237600000000",
    )
    officier_user = upsert_user(
        "officier@civilconnect.cm",
        User.Role.OFFICIER_EC,
        telephone="+237600000001",
    )
    upsert_user(
        "archiviste@civilconnect.cm",
        User.Role.ARCHIVISTE,
        telephone="+237600000002",
    )
    upsert_user(
        "adminbunec@civilconnect.cm",
        User.Role.ADMIN_BUNEC,
        telephone="+237600000003",
    )
    upsert_user(
        "maire@civilconnect.cm",
        User.Role.MAIRE,
        telephone="+237600000004",
    )
    upsert_user(
        "secu@civilconnect.cm",
        User.Role.RESP_SEC,
        telephone="+237600000005",
    )
    hopital_user = upsert_user(
        "hopital@civilconnect.cm",
        User.Role.HOPITAL,
        telephone="+237600000006",
    )
    mairie, _ = Mairie.objects.get_or_create(
        code="CMR001",
        defaults={
            "nom": "Mairie Demo",
            "region": "Centre",
            "departement": "Demo",
            "commune": "Demo",
        },
    )
    OfficierEC.objects.get_or_create(
        user=officier_user,
        defaults={
            "matricule": "OFF001",
            "cle_certification_bunec": "BUNEC-DEMOCLE",
        },
    )
    from hopitaux.models import Hopital  # noqa: E402

    Hopital.objects.get_or_create(
        user=hopital_user,
        defaults={
            "code": "HOP001",
            "nom": "Hôpital Démo",
            "adresse": "Avenue Demo",
            "ville": "Yaoundé",
        },
    )
    print("Comptes créés / mis à jour (mot de passe commun :", DEFAULT_PASSWORD + "):")
    print("  Citoyen           : citoyen@civilconnect.cm")
    print("  Officier EC       : officier@civilconnect.cm")
    print("  Archiviste        : archiviste@civilconnect.cm")
    print("  Admin BUNEC       : adminbunec@civilconnect.cm")
    print("  Maire             : maire@civilconnect.cm")
    print("  Resp. sécurité    : secu@civilconnect.cm")
    print("  Hôpital           : hopital@civilconnect.cm")
    print("  Mairie (réf.)     :", mairie.code, mairie.nom)
    print()
    print("Pour se connecter SANS code MFA (démo), lance le backend avec :")
    print("  set DEMO_SKIP_MFA=1")
    print()
    print("Pour tester le MFA (secret + code TOTP), en local :")
    print("  python manage.py show_mfa_secret citoyen@civilconnect.cm --create")
    print()
    print("Code MFA de test (bypass, si DEMO_MFA_BYPASS_CODE est défini + DEBUG) : 888888")
    print("  (variable d'environnement DEMO_MFA_BYPASS_CODE — tu peux en mettre un autre pour d'autres scénarios)")


if __name__ == "__main__":
    main()
