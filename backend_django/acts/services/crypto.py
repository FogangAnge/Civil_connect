import base64
import hashlib
import json
import os
from pathlib import Path

import qrcode
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings


class RSAService:
    @staticmethod
    def generate_key_pair() -> tuple[str, str]:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode('utf-8')
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('utf-8')
        return private_pem, public_pem

    @staticmethod
    def sign_data(private_pem: str, data: str) -> str:
        private_key = serialization.load_pem_private_key(private_pem.encode('utf-8'), password=None)
        signature = private_key.sign(
            data.encode('utf-8'),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify_signature(public_pem: str, data: str, signature_b64: str) -> bool:
        public_key = serialization.load_pem_public_key(public_pem.encode('utf-8'))
        try:
            public_key.verify(
                base64.b64decode(signature_b64),
                data.encode('utf-8'),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False


class AESService:
    @staticmethod
    def encrypt(plaintext: str, key: bytes) -> tuple[str, str]:
        if len(key) != 32:
            raise ValueError('AES key must be 32 bytes (256 bits).')
        aes = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aes.encrypt(nonce, plaintext.encode('utf-8'), None)
        return base64.b64encode(ciphertext).decode('utf-8'), base64.b64encode(nonce).decode('utf-8')

    @staticmethod
    def decrypt(ciphertext_b64: str, nonce_b64: str, key: bytes) -> str:
        if len(key) != 32:
            raise ValueError('AES key must be 32 bytes (256 bits).')
        aes = AESGCM(key)
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        plaintext = aes.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')


def generate_qr_code(acte_uuid: str, numero_acte: str, date_str: str, mairie: str) -> tuple[str, str]:
    payload = json.dumps(
        {'uuid': acte_uuid, 'numero': numero_acte, 'date': date_str, 'mairie': mairie},
        ensure_ascii=False,
        separators=(',', ':'),
    )
    sha256_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    media_root = Path(getattr(settings, 'MEDIA_ROOT', Path.cwd() / 'media'))
    out_dir = media_root / 'qrcodes'
    out_dir.mkdir(parents=True, exist_ok=True)
    image_path = out_dir / f'{acte_uuid}.png'

    img = qrcode.make(payload)
    img.save(image_path)

    return sha256_hash, str(image_path)

