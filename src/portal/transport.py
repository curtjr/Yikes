import socket
import json
import select
import base64
import threading
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
from portal.auth import Authenticator

host = "0.0.0.0"
max_connections = 10

class SocketHandler:
    def send_message(self, sock, message_dict):
        raw = json.dumps(message_dict).encode()
        sock.sendall(raw)

    def receive_message(self, sock, timeout=0.1):
        ready, _, _ = select.select([sock], [], [], timeout)
        if not ready:
            return None
        data = b""
        try:
            chunk = sock.recv(4096)
            if chunk:
                data += chunk
        except BlockingIOError:
            pass
        return data.decode("utf-8", errors="ignore")
    
    def send_encrypted(self, sock, fernet, message_dict):
        plaintext = json.dumps(message_dict).encode("utf-8")
        ciphertext = fernet.encrypt(plaintext)
        sock.sendall(ciphertext)

    def receive_encrypted(self, sock, fernet, bufsize=4096):
        ciphertext = sock.recv(bufsize)
        if not ciphertext:
            return None
        plaintext = fernet.decrypt(ciphertext)
        return json.loads(plaintext.decode("utf-8"))

class Client(SocketHandler):
    def __init__(self, host, port):
        super().__init__()  
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.new_keys()  # Generate new RSA keys for encryption
        self.encrypted_key_dict = {
        "fernet_key": base64.b64encode(self.encrypted_key).decode()
        }

        self.send_message(self.sock, self.encrypted_key_dict)

        # Prepare authenticator with your credential store
        self.auth = Authenticator()

    def new_keys(self):
        with open("public_key.pem", "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
            fernet_key = Fernet.generate_key()
            self.fernet = Fernet(fernet_key)
            self.encrypted_key = public_key.encrypt(
            fernet_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )

    def authenticate(self, username: str, password: str):
        # Sends credentials and waits for server approval.
        return self.auth.client_handshake(self, self.sock, self.fernet, username, password)

class ClientSession():
    def __init__(self, sock, addr, fernet_key):
        self.sock = sock
        self.addr = addr
        self.fernet = Fernet(fernet_key)

class Server(SocketHandler):
    def __init__(
        self,
        host: str,
        port: int,
        auth_store: dict,
        on_client_connect=None,
        max_connections: int = 10
    ):
        super().__init__()  
        self.auth = Authenticator(auth_store)
        self.on_client_connect = on_client_connect

        # Create and bind the listening socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(max_connections)

        self.clients = []

        self.new_keys() # Generate new RSA keys for encryption

        print(f"Server listening on {host}:{port}")

    def new_keys(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()

        with open("public_key.pem", "wb") as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    def run(self):
        try:
            while True:
                conn, addr = self.server.accept()
                print(f"Connection from {addr}")
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True  # Optional: lets program exit even if thread is running
                thread.start()
        finally:
            self.server.close()

    def handle_client(self, conn, addr):
        try:
            key_json = self.receive_message(conn)
            key_dict = json.loads(key_json)
            encrypted_key = base64.b64decode(key_dict["fernet_key"])

            fernet_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            fernet = Fernet(fernet_key)

            # Run the auth handshake over that socket
            if self.auth.server_handshake(self, conn, fernet):
                print(f"Client {addr} authenticated successfully.")
                session = ClientSession(conn, addr, fernet_key)
                self.clients.append(session)
                if self.on_client_connect:
                    self.on_client_connect(self, addr)
            else:
                print(f"Client {addr} failed authentication.")

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            conn.close()

