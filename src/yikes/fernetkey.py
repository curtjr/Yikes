from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet

class FernetKey():
    def __init__(self):
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.fernet_key)
        self.encrypted_key = self.public_key.encrypt(
            self.fernet_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),label=None
                )
            )