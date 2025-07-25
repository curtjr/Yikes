import jwt
import base64
import socket
import threading
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet

class Authenticator:
    def new_client_key(self):
        fernet_key = Fernet.generate_key()
        self.fernet = Fernet(fernet_key)
        self.encrypted_key = self.public_key.encrypt(fernet_key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))

    def new_server_keys(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()

        public_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public_key.pem")

        with open(public_key_file, "wb") as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    def client_handshake(self):
        try:
            self.public_key = None
            while self.public_key is None:
                self.public_key = self.receive_public_key(self.sock)
            
            self.new_client_key()
            self.send_key(self.sock, self.encrypted_key)
            print("Client handshake successful")
            return True
        except Exception as e:
            print(f"Client handshake error: {e} -client")
            return False

    def server_handshake(self, sock, addr):
        # send your public key once
        der_bytes = self.public_key.public_bytes(encoding=serialization.Encoding.DER,format=serialization.PublicFormat.SubjectPublicKeyInfo)
        self.send_key(sock, der_bytes)

        key_bytes = None
        while key_bytes is None:
            key_bytes = self.receive_fernet_key(sock)
            
        fernet_key = self.private_key.decrypt(
            key_bytes,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        try:
            self.fernet = Fernet(fernet_key)
            print(f"Client {addr} authenticated successfully.")
            
            return True, fernet_key
        except Exception:
            print(f"Client {addr} failed authentication.")
            return False