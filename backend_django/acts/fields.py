import base64
from django.conf import settings
from django.db import models

from .services.crypto import AESService


class EncryptedCharField(models.CharField):
    """
    Stocke une valeur chiffrée (AESGCM) dans la DB, retourne du clair dans Python.
    """

    def from_db_value(self, value, expression, connection):
        if value is None or value == '':
            return value
        try:
            key_b64 = getattr(settings, 'AES_KEY_B64', '') or ''
            if not key_b64:
                return value
            key = base64.b64decode(key_b64)
            ciphertext_b64, nonce_b64 = value.split('.', 1)
            return AESService.decrypt(ciphertext_b64, nonce_b64, key)
        except Exception:
            return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None or value == '':
            return value
        key_b64 = getattr(settings, 'AES_KEY_B64', '') or ''
        if not key_b64:
            return value
        key = base64.b64decode(key_b64)
        ciphertext_b64, nonce_b64 = AESService.encrypt(str(value), key)
        return f'{ciphertext_b64}.{nonce_b64}'

