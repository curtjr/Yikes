import socket
import struct
import json
import base64
from cryptography.hazmat.primitives import serialization

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
    def send_json(self, sock: socket.socket, json_obj):
        """
            Simplified version of send_data for sending jsons as base64 encoded bytes.

            Args:
                sock(socket.socket): Target socket.
                json_obj(json): Json object
        """
        json_str = json.dumps(json_obj)
        json_bytes = base64.b64encode(json_str.encode())
        self.send_data(sock, json_bytes)

    def recv_json(self, sock: socket.socket):
        """
            Simplified version of recv_data for receiving jsons that are base64 encoded bytes.

            Args:
                sock(socket.socket): Target socket.

            Returns:
                json_obj(json): Json object.
        """
        json_bytes = self.recv_data(sock)
        json_str = base64.b64decode(json_bytes).decode()
        json_obj = json.loads(json_str)
        return json_obj

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

    def recv_data(self, sock: socket.socket):
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

def send_key(sock: socket.socket, key_bytes: bytes):
    try:
        length = len(key_bytes)
        header = struct.pack('>I', length)
        sock.sendall(header + key_bytes)
    except Exception as e:
        print(f"Error sending key {e}")

def receive_public_key(sock: socket.socket):
    try:
        header = recv_exact(sock, 4) # Get header (has length of key)
        length, = struct.unpack(">I", header) # Length of key

        der_bytes = recv_exact(sock, length) # Receive key
        public_key = serialization.load_der_public_key(der_bytes) # Deserialize key
        return public_key
    except Exception as e:
        print(f"Error receiving public key: {e}")
    
def receive_fernet_key(sock: socket.socket):
    try:
        header = recv_exact(sock, 4)
        length, = struct.unpack(">I", header)

        key_bytes = recv_exact(sock, length)
        return key_bytes
    except Exception as e:
        print(f"Error receiving fernet key {e}")
    