import socket
import socket
import struct
import json
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from yikes.rsakey import RSAKey
from yikes.fernetkey import FernetKey
from yikes.server import Server

class Transport():
    def __init__(self,addr:tuple, max_connections:int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = addr
        self.max_connections = max_connections

        self.connections = {}
        self.listeners = []

        self.RK = None
        self.private_key = None
        self.public_key = None

        self.FK = None
        self.fernet_key = None

    def start_client(self):
        self.sock.connect(self.addr)
        self.sock.setblocking(True)

        self.FK = FernetKey()
        self.fernet_key = self.FK.key
        while self.public_key is None:
            self.public_key = self.receive_public_key(self.sock)
        
        self.new()
        self.send_key(self.sock, self.FK.encrypted_key)
        
    def start_server(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.addr)
        if self.max_connections == 0:
            self.sock.listen(socket.SOMAXCONN)
        else:
            self.sock.listen(self.max_connections)

        self.RK = RSAKey()

        self.private_key = self.RK.private_key
        self.public_key = self.RK.public_key

        self.send_key(self.sock, self.RK.public_key_bytes_der)

        key_bytes = None
        while key_bytes is None:
            key_bytes = self.receive_fernet_key(self.sock)
            
        self.fernet_key = self.RK.private_key_decrypt(key_bytes)

        try:
            while True:
                sock, addr = self.sock.accept()
                self.connections[addr] = sock
                self.notify_listeners(sock, addr)
        finally:
            self.sock.close()

    def notify_listeners(self, sock: socket.socket, addr):
        for callback in self.listeners:
            callback(sock, addr)
        
    def receive_public_key(self):
        header = self.recv_exact(self.sock, 4) # Get header (has length of key)
        length, = struct.unpack(">I", header) # Length of key

        der_bytes = self.recv_exact(self.sock, length) # Receive key
        public_key = serialization.load_der_public_key(der_bytes) # Deserialize key
        return public_key
        
    def receive_fernet_key(self):
        header = self.recv_exact(self.sock, 4)
        length, = struct.unpack(">I", header)

        key_bytes = self.recv_exact(self.sock, length)
        return key_bytes
    
    def recv_exact(self, length: int):
        """Receive exactly 'length' bytes from a socket."""
        data = b""
        while len(data) < length:
            chunk = self.sock.recv(length - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before full data received")
            data += chunk
        return data

    def send_json(self, json_obj):
        """
            Simplified version of send_data for sending jsons as base64 encoded bytes.

            Args:
                sock(socket.socket): Target socket.
                json_obj(json): Json object
        """
        json_str = json.dumps(json_obj)
        json_bytes = base64.b64encode(json_str.encode())
        self.send_data(self.sock, json_bytes)

    def recv_json(self):
        """
            Simplified version of recv_data for receiving jsons that are base64 encoded bytes.

            Args:
                sock(socket.socket): Target socket.

            Returns:
                json_obj(json): Json object.
        """
        json_bytes = self.recv_data(self.sock)
        json_str = base64.b64decode(json_bytes).decode()
        json_obj = json.loads(json_str)
        return json_obj

    def send_bytes(self, bytes: bytes):
        """
        Encrypts data using a Fernet, and sends the data over a socket.

        Args:
            sock(socket.socket): Socket to encrypt and send data through.
            data(bytes): Data that will be encrypted and sent.
        """
        try:
            ciphertext = self.fernet.encrypt(bytes)
            length = len(ciphertext)
            header = struct.pack(">I", length)
            self.sock.sendall(header + ciphertext)
        except Exception as e:
            print(f"Error sending bytes: {e}")

    def recv_bytes(self):
        """
        Waits for and receives data from a socket, and decrypts the data using a Fernet.

        Args:
            sock(socket.socket): Socket to encrypt and send data through.

        Returns:
            data(bytes): Data received from the socket
        """
        try:
            header = self.recv_exact(self.sock, 4)
            length, = struct.unpack(">I", header)
            ciphertext = self.recv_exact(self.sock, length)

            bytes = self.fernet.decrypt(ciphertext)
            return bytes
        except Exception as e:
            print(f"Error receiving bytes: {e}")

    def send_key(self, key_bytes: bytes):
        try:
            length = len(key_bytes)
            header = struct.pack('>I', length)
            self.sock.sendall(header + key_bytes)
        except Exception as e:
            print(f"Error sending key {e}")