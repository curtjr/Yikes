import socket
import json
import base64
import threading
import os
from cryptography.fernet import Fernet
from portal.auth import Authenticator
from portal.socks import SocketHandler

"'CLIENT'"
class Client(SocketHandler,Authenticator):
    def __init__(self, host, port, callback=None):
        super().__init__()  
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.callback = callback
        
    def run_client(self):
        self.sock.connect((self.host, self.port))
        self.sock.setblocking(True)

        print("Client connecting to server at", self.host, ":", self.port)
        
        success = self.client_handshake()
        if success and self.callback:
            self.callback()
            

"'SERVER'"
clients = []
class Server(SocketHandler,Authenticator):
    def __init__(self, host, port, callback=None):
        super().__init__()  
        self.callback = callback

        self.max_connections = 5  # Default max connections

        # Create and bind the listening socket
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((host, port))
        self.server_sock.listen(self.max_connections)

        self.new_server_keys() # Generate new RSA keys for encryption

        print(f"Server listening on {host}:{port}")

    def run_server(self):
        try:
            while True:
                sock, addr = self.server_sock.accept()
                print(f"Connection from {addr}")
                HandleClient = ClientHandler(self, sock, addr, self.callback)
                HandleClient.start()
        finally:
            self.server_sock.close()
        
    def close_sock(self, sock):
        sock.close()

    def set_max_connections(self, max_connections):
        self.max_connections = max_connections
        self.server.listen(max_connections)

class ClientHandler(threading.Thread):
    def __init__(self, server: Server, sock, addr, callback):
        super().__init__(daemon=True)
        try:
            success, fernet_key = server.server_handshake(sock,addr)
            print(f"handshake successful: {success}")
            if success:
                session = self.Session(sock,addr,fernet_key,threading.current_thread)
                if callback:
                    callback(session)
        except Exception as e:
            print(f"Error handling client {addr}: {e}")

    class Session:
        def __init__(self, sock:socket.socket, addr:str, fernet_key:Fernet, thread:threading.Thread):
            self.sock = sock
            self.addr = addr
            self.fernet = Fernet(fernet_key)
            self.thread = thread
            self.lock = threading.Lock
            global clients
            clients.append(self)