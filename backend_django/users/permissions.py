from __future__ import annotations

from functools import wraps
from typing import Callable

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


ROLE_PERMISSIONS = {
    'CITOYEN': {'can_create_demand', 'can_view_own_acts', 'can_verify_qr'},
    'OFFICIER_EC': {
        'can_create_act',
        'can_sign_act',
        'can_validate_demand',
        'can_view_mairie_acts',
        'can_request_correction',
        'can_view_hospital_declarations',
    },
    'MAIRE': {
        'can_create_act',
        'can_sign_act',
        'can_validate_demand',
        'can_view_mairie_acts',
        'can_request_correction',
        'can_manage_mairie_users',
        'can_generate_reports',
        'can_view_all_mairie_acts',
        'can_view_hospital_declarations',
    },
    'ARCHIVISTE': {'can_upload_ocr', 'can_validate_ocr', 'can_view_archives'},
    'ADMIN_BUNEC': {
        'can_view_all_mairies',
        'can_manage_all_users',
        'can_export_national_stats',
        'can_create_act',
        'can_sign_act',
        'can_validate_demand',
        'can_view_mairie_acts',
        'can_request_correction',
        'can_upload_ocr',
        'can_validate_ocr',
        'can_view_archives',
        'can_create_demand',
        'can_view_own_acts',
        'can_verify_qr',
    },
    'RESP_SEC': {'can_view_audit_logs', 'can_manage_mfa', 'can_run_security_reports'},
    'HOPITAL': {'can_create_hospital_declaration', 'can_view_hospital_declarations'},
}


def has_permission(user, perm: str) -> bool:
    role = getattr(user, 'role', None) or ''
    return perm in ROLE_PERMISSIONS.get(role, set())


class RBACPermission(BasePermission):
    """
    Permission DRF: nécessite une permission déclarée via view.required_permissions.
    """

    message = "Accès refusé: permissions insuffisantes."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        required = getattr(view, 'required_permissions', None)
        if not required:
            return True
        return all(has_permission(request.user, p) for p in required)


def require_permission(permission_name: str) -> Callable:
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                raise PermissionDenied("Vous devez être connecté.")
            if not has_permission(request.user, permission_name):
                raise PermissionDenied(f"Accès refusé: {permission_name} requis.")
            return fn(self, request, *args, **kwargs)

        return wrapper

    return decorator

