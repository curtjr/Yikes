import jwt
import base64
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
        self.public_key = None
        while self.public_key is None:
            self.public_key = self.receive_public_key(self.sock)

        print("Public key received")
        
        self.new_client_key()
        print("Client encrypted fernet")
        self.send_key(self.sock, self.encrypted_key)
        print("Client sent key")

    def server_handshake(self, conn, addr):
        # send your public key once
        der_bytes = self.public_key.public_bytes(encoding=serialization.Encoding.DER,format=serialization.PublicFormat.SubjectPublicKeyInfo)
        self.send_key(conn, der_bytes)
        print("Server sent public key")

        key_bytes = self.receive_fernet_key(conn)
        print("Server received client fernet")
            
        fernet_key = self.private_key.decrypt(
            key_bytes,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print("Server decrypted fernet")

        try:
            self.fernet = Fernet(fernet_key)
            print(f"Client {addr} authenticated successfully.")
            return True
        except Exception:
            print(f"Client {addr} failed authentication.")
            return False
            
        


class StaticTokenAuthenticator:
    def __init__(self, valid_tokens):
        self.valid_tokens = set(valid_tokens)

    def client_handshake(self, transport, token):
        transport.send_message({"type": "token", "token": token})
        while True:
            msg = transport.receive_message()
            if not msg:
                continue
            if msg.get("type") != "token":
                continue
            return msg.get("status") == "success"

    def server_handshake(self, transport):
        while True:
            msg = transport.receive_message()
            if not msg:
                continue
            if msg.get("type") != "token":
                continue

            presented = msg.get("token")
            ok = presented in self.valid_tokens
            status = "success" if ok else "failed"
            transport.send_message({"type": "token", "status": status})
            return ok
    