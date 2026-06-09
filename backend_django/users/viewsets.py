import os

import pyotp
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

MFA_PREAUTH_SALT = 'civilconnect-mfa-preauth'
MFA_PREAUTH_MAX_AGE = 300


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['POST'], url_path='login')
    def login(self, request):
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({'detail': 'Identifiants invalides.'}, status=401)

        if os.getenv('DEMO_SKIP_MFA', '0') == '1':
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            resp = Response({'mfa_required': False, 'role': getattr(user, 'role', 'CITOYEN')})
            resp.set_cookie(
                getattr(settings, 'JWT_AUTH_COOKIE', 'cc_access'),
                access,
                httponly=True,
                samesite='Lax',
            )
            resp.set_cookie(
                getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', 'cc_refresh'),
                str(refresh),
                httponly=True,
                samesite='Lax',
            )
            return resp

        if not getattr(user, 'mfa_secret', ''):
            user.mfa_secret = pyotp.random_base32()
            user.mfa_enabled = True
            user.save(update_fields=['mfa_secret', 'mfa_enabled'])

        request.session['preauth_user_id'] = user.id
        signer = TimestampSigner(salt=MFA_PREAUTH_SALT)
        preauth_token = signer.sign(str(user.id))
        # Jeton signé : évite l’échec si le cookie de session n’est pas renvoyé (SPA cross-origin localhost/127.0.0.1).
        return Response({'mfa_required': True, 'preauth_token': preauth_token})

    @action(detail=False, methods=['POST'], url_path='mfa-verify')
    def mfa_verify(self, request):
        code = (request.data.get('code') or '').strip()
        user_id = None
        token = (request.data.get('preauth_token') or '').strip()
        if token:
            try:
                signer = TimestampSigner(salt=MFA_PREAUTH_SALT)
                user_id = int(signer.unsign(token, max_age=MFA_PREAUTH_MAX_AGE))
            except (BadSignature, SignatureExpired, ValueError):
                return Response({'detail': 'Étape MFA expirée. Reconnectez-vous.'}, status=401)
        else:
            user_id = request.session.get('preauth_user_id')
        if not user_id:
            return Response({'detail': 'Session expirée. Reconnectez-vous.'}, status=401)

        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'Utilisateur introuvable.'}, status=401)

        totp = pyotp.TOTP(user.mfa_secret)
        bypass = (getattr(settings, 'DEMO_MFA_BYPASS_CODE', '') or '').strip()
        dev_ok = settings.DEBUG or os.getenv('ALLOW_DEMO_MFA_BYPASS', '0') == '1'
        mfa_ok = bool(bypass and dev_ok and code == bypass) or totp.verify(code, valid_window=1)
        if not mfa_ok:
            return Response({'detail': 'Code MFA invalide.'}, status=401)

        request.session.pop('preauth_user_id', None)

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        resp = Response({'role': getattr(user, 'role', 'CITOYEN')})
        resp.set_cookie(getattr(settings, 'JWT_AUTH_COOKIE', 'cc_access'), access, httponly=True, samesite='Lax')
        resp.set_cookie(getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', 'cc_refresh'), str(refresh), httponly=True, samesite='Lax')
        return resp

    @action(detail=False, methods=['POST'], url_path='refresh')
    def refresh(self, request):
        refresh_cookie = request.COOKIES.get(getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', 'cc_refresh'))
        if not refresh_cookie:
            return Response({'detail': 'Refresh token manquant.'}, status=401)
        try:
            refresh = RefreshToken(refresh_cookie)
            access = str(refresh.access_token)
        except Exception:
            return Response({'detail': 'Refresh token invalide.'}, status=401)

        resp = Response({'status': 'ok'})
        resp.set_cookie(getattr(settings, 'JWT_AUTH_COOKIE', 'cc_access'), access, httponly=True, samesite='Lax')
        return resp

