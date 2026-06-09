import hashlib
import json

from django.utils.deprecation import MiddlewareMixin

from .models import AuditLog


class AuditMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.method not in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return response

        try:
            raw = request.body or b''
            payload_hash = hashlib.sha256(raw).hexdigest() if raw else ''
        except Exception:
            payload_hash = ''

        try:
            user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
            ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')
            AuditLog.objects.create(
                user=user,
                action=request.method,
                endpoint=request.path,
                ip=str(ip)[:64],
                payload_hash=payload_hash,
            )
        except Exception:
            # Ne jamais bloquer la requête à cause de l’audit
            pass

        return response

