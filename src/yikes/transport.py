import socket
import struct
import json
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet
from yikes.rsakey import RSAKey
from yikes.fernetkey import FernetKey

class Transport():
    def __init__(self,addr:tuple, mode:str):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = addr
        self.max_connections = 0

        if mode == "s":
            self.mode = "s"
        else:
            self.mode = "c"

        self.connections = {}
        self.listeners = []

        self.RK = None
        self.private_key = None
        self.public_key = None

        self.FK = None
        self.fernet = None

        # Only create an RSA keypair for server mode. Clients will receive
        # the server's public key during the handshake.
        if self.mode == "s":
            self.RK = RSAKey()
            self.private_key = self.RK.private_key
            self.public_key = self.RK.public_key
        else:
            self.RK = None
            self.private_key = None
            self.public_key = None

    def start_client(self):
        self.sock.connect(self.addr)
        self.sock.setblocking(True)

        self.FK = FernetKey()
        self.fernet_key = self.FK.key
        while self.public_key is None:
            self.public_key = self.receive_public_key(self.sock)
        
        self.send_key(self.sock, self.FK.encrypt_key(self.public_key))
        # initialize a local Fernet instance for the client side
        self.fernet = Fernet(self.fernet_key)
        
    def start_server(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.addr)
        if self.max_connections == 0:
            self.sock.listen(socket.SOMAXCONN)
        else:
            self.sock.listen(self.max_connections)

        try:
            while True:
                sock, addr = self.sock.accept()
                # create a per-connection entry (avoid KeyError)
                self.connections[addr] = {"socket": sock}
                self.handle_client(sock, addr)
                self.notify_listeners(sock, addr)
        finally:
            self.sock.close()

    def handle_client(self, sock: socket.socket, addr):
        self.send_key(sock, self.RK.public_key_bytes_der)

        key_bytes = None
        while key_bytes is None:
            key_bytes = self.receive_fernet_key(sock)
            
        fernet = Fernet(self.RK.private_key_decrypt(key_bytes))
        # attach the per-connection Fernet object while preserving the socket
        if addr in self.connections:
            self.connections[addr]["fernet"] = fernet
        else:
            self.connections[addr] = {"fernet": fernet}

    def notify_listeners(self, sock: socket.socket, addr):
        for callback in self.listeners:
            callback(sock, addr)
        
    def receive_public_key(self, sock: socket.socket):
        header = self.recv_exact(sock, 4) # Get header (has length of key)
        length, = struct.unpack(">I", header) # Length of key

        der_bytes = self.recv_exact(sock, length) # Receive key
        public_key = serialization.load_der_public_key(der_bytes) # Deserialize key
        return public_key
        
    def receive_fernet_key(self, sock: socket.socket):
        header = self.recv_exact(sock, 4)
        length, = struct.unpack(">I", header)

        key_bytes = self.recv_exact(sock, length)
        return key_bytes
    
    def recv_exact(self, sock: socket.socket, length: int):
        """Receive exactly 'length' bytes from a socket."""
        data = b""
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before full data received")
            data += chunk
        return data

    def send_bytes(self, bytes: bytes, addr=None):
        """
        Encrypts data using a Fernet, and sends the data over a socket.

        Args:
            sock(socket.socket): Socket to encrypt and send data through.
            data(bytes): Data that will be encrypted and sent.
        """
        try:
            if self.mode == "s":
                sock = self.connections[addr]["socket"]
                fernet = self.connections[addr]["fernet"]
            else:
                fernet = self.fernet
                sock = self.sock
            encrypted_bytes = fernet.encrypt(bytes)
            length = len(encrypted_bytes)
            header = struct.pack(">I", length)
            sock.sendall(header + encrypted_bytes)
        except Exception as e:
            print(f"Error sending bytes: {e}")

    def recv_bytes(self, addr=None) -> bytes:
        """
        Waits for and receives data from a socket, and decrypts the data using a Fernet.

        Args:
            sock(socket.socket): Socket to encrypt and send data through.

        Returns:
            data(bytes): Data received from the socket
        """
        try:
            if self.mode == "s":
                sock = self.connections[addr]["socket"]
                fernet = self.connections[addr]["fernet"]
            else:
                fernet = self.fernet
                sock = self.sock
            header = self.recv_exact(sock, 4)
            length, = struct.unpack(">I", header)
            encrypted_bytes = self.recv_exact(sock, length)

            bytes = fernet.decrypt(encrypted_bytes)
            return bytes
        except Exception as e:
            print(f"Error receiving bytes: {e}")

    def send_key(self, sock: socket.socket, key_bytes: bytes):
        try:
            length = len(key_bytes)
            header = struct.pack('>I', length)
            sock.sendall(header + key_bytes)
        except Exception as e:
            print(f"Error sending key {e}")