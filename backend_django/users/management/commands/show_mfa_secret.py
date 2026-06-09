"""
Affiche le secret TOTP, l'URI otpauth:// et le code courant — uniquement en dev.

Usage:
  set ALLOW_DEV_MFA_EXPORT=1
  python manage.py show_mfa_secret citoyen@civilconnect.cm

Ou avec DEBUG=True dans settings (développement local).
"""
import os

import pyotp
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Affiche secret TOTP / URI d'enrôlement (DEBUG ou ALLOW_DEV_MFA_EXPORT=1 uniquement)."

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Email du compte")
        parser.add_argument(
            "--create",
            action="store_true",
            help="Génère un secret MFA s'il est absent (équivalent au premier login sans skip).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and os.environ.get("ALLOW_DEV_MFA_EXPORT") != "1":
            raise CommandError(
                "Refusé : en production, ne pas exposer les secrets MFA. "
                "En local : DEBUG=True dans settings, ou ALLOW_DEV_MFA_EXPORT=1."
            )

        email = (options["email"] or "").strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise CommandError(f"Aucun utilisateur avec l'email : {email!r}")

        if not user.mfa_secret:
            if options["create"]:
                user.mfa_secret = pyotp.random_base32()
                user.mfa_enabled = True
                user.save(update_fields=["mfa_secret", "mfa_enabled"])
                self.stdout.write(self.style.WARNING("Secret MFA généré (--create)."))
            else:
                raise CommandError(
                    "Pas encore de secret MFA pour ce compte. "
                    "Connecte-toi une fois (mot de passe) pour en créer un, ou relance avec --create."
                )

        totp = pyotp.TOTP(user.mfa_secret)
        uri = totp.provisioning_uri(name=user.email, issuer_name="CivilConnect")
        code = totp.now()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Utilisateur : {user.email}"))
        self.stdout.write(f"Secret (base32) : {user.mfa_secret}")
        self.stdout.write("")
        self.stdout.write("URI d'enrôlement (QR / import dans l'appli) :")
        self.stdout.write(uri)
        self.stdout.write("")
        self.stdout.write(f"Code TOTP actuel (valide ~30 s) : {code}")
        self.stdout.write("")
        self.stdout.write(
            "Ajoute ce compte dans Google Authenticator ou Microsoft Authenticator "
            "(scan du QR généré à partir de l'URI, ou saisie manuelle du secret)."
        )
