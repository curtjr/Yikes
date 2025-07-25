import socket
import struct
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet

def recv_exact(sock: socket.socket, length: int):
    """Receive exactly 'length' bytes from a socket."""
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise ConnectionError("Connection closed before full data received")
        data += chunk
    return data

class SocketHandler:
    def send_key(self, sock: socket.socket, key_bytes: bytes):
        try:
            length = len(key_bytes)
            header = struct.pack('>I', length)
            sock.sendall(header + key_bytes)
        except Exception as e:
            print(f"Error sending key {e}")

    def receive_public_key(self, sock: socket.socket):
        try:
            header = recv_exact(sock, 4) # Get header (has length of key)
            length, = struct.unpack(">I", header) # Length of key

            der_bytes = recv_exact(sock, length) # Receive key
            public_key = serialization.load_der_public_key(der_bytes) # Deserialize key
            return public_key
        except Exception as e:
            print(f"Error receiving public key: {e}")
    
    def receive_fernet_key(self, sock: socket.socket):
        try:
            header = recv_exact(sock, 4)
            length, = struct.unpack(">I", header)

            key_bytes = recv_exact(sock, length)
            return key_bytes
        except Exception as e:
            print(f"Error receiving fernet key {e}")

    def send_data(self, sock: socket.socket, data: bytes):
        """
        Encrypts data using a Fernet, and sends the data over a socket.

        Args:
            sock(socket.socket): Socket to encrypt and send data through.
            data(bytes): Data that will be encrypted and sent.
        """
        try:
            ciphertext = self.fernet.encrypt(data)
            length = len(ciphertext)
            header = struct.pack(">I", length)
            sock.sendall(header + ciphertext)
        except Exception as e:
            print(f"Error sending data: {e}")

    def receive_data(self, sock: socket.socket):
        """
        Waits for and receives data from a socket, and decrypts the data using a Fernet.

        Args:
            sock(socket.socket): Socket to encrypt and send data through.

        Returns:
            data(bytes): Data received from the socket
        """
        try:
            header = recv_exact(sock, 4)
            length, = struct.unpack(">I", header)
            ciphertext = recv_exact(sock, length)

            data = self.fernet.decrypt(ciphertext)
            return data
        except Exception as e:
            print(f"Error receiving data: {e}")

