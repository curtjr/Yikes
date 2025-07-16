import socket
import json
import base64
import threading
import os
from cryptography.fernet import Fernet
from portal.auth import Authenticator
from portal.socks import SocketHandler

class Client(SocketHandler,Authenticator):
    def __init__(self, host, port):
        super().__init__()  
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.setblocking(True)

        print("Client connecting to server at", host, ":", port)
        
        self.client_handshake()

class Server(SocketHandler,Authenticator):
    def __init__(self, host, port, on_client_connect=None):
        super().__init__()  
        self.on_client_connect = on_client_connect

        self.max_connections = 5  # Default max connections

        # Create and bind the listening socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(self.max_connections)
        self.clients = []

        self.new_server_keys() # Generate new RSA keys for encryption

        print(f"Server listening on {host}:{port}")

    def start(self):
        try:
            while True:
                conn, addr = self.server.accept()
                print(f"Connection from {addr}")
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True  # Optional: lets program exit even if thread is running
                thread.start()
        finally:
            self.server.close()

    def handle_client(self,conn,addr):
        try:
            success = self.server_handshake(conn,addr)
            if success and self.on_client_connect:
                self.on_client_connect(self, conn, addr)
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            conn.close()

    def set_max_connections(self, max_connections):
        self.max_connections = max_connections
        self.server.listen(max_connections)

    class ClientSession:
        def __init__(self, sock, addr, fernet_key):
            self.sock = sock
            self.addr = addr
            self.fernet = Fernet(fernet_key)

