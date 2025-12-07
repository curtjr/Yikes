from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet


class FernetKey():
    def __init__(self):
        # raw key bytes and a Fernet instance ready for local encrypt/decrypt
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        self.encrypted_key = None

    def encrypt_key(self, public_key):
        """Encrypt the raw Fernet key bytes using the provided RSA public key."""
        self.encrypted_key = public_key.encrypt(
            self.key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return self.encrypted_key

    def decrypt(self, encrypted_bytes: bytes):
        return self.fernet.decrypt(encrypted_bytes)

    def encrypt(self, unencrypted_bytes: bytes):
        return self.fernet.encrypt(unencrypted_bytes)