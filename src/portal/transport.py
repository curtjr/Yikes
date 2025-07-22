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
    """
    Client class used for connecting to a server.
    To create a client please use the create_client() function!
    """
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
    """
    Server class used for accepting client connections.
    To create a server please use the create_server() function!
    """
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
        
    def close_sock(self, sock:socket.socket):
        """
        Closes the provided socket.
        
        Args:
            sock(socket.socket): The socket you want to close.
        """
        sock.close()

    def get_clients(self):
        """
        Returns a list of client sessions that are currently connected to the server.

        Returns:
            List[Session]: A list containing:
                - A list of Session classes
        """
        return clients

    def set_max_connections(self, max_connections):
        """
        Sets the maximum number of clients allowed to connect to the server. If the current number is equal to or above the maximum no new connection attempts will be accepted.
        
        Args:
            max_connections(int): Maximum number of connections
        """
        self.max_connections = max_connections
        self.server.listen(max_connections)

class Session:
        """
        Session class used for simplifying and managing client connections to the server.

        Args:
            sock(socket.socket): Socket shared between client and server.
            addr(str): Client address.
            fernet_key(Fernet): Fernet key for encryption between client and server.
            thread(threading.thread): Thread the client is operating in.
        """
        def __init__(self, sock:socket.socket, addr:str, fernet_key:Fernet, thread:threading.Thread):
            self.sock = sock
            self.addr = addr
            self.fernet = Fernet(fernet_key)
            self.thread = thread
            self.lock = threading.Lock
            global clients
            clients.append(self)

class ClientHandler(threading.Thread):
    """
    Class the server uses to handle client Sessions.
    """
    def __init__(self, server: Server, sock, addr, callback):
        super().__init__(daemon=True)
        try:
            success, fernet_key = server.server_handshake(sock,addr)
            if success:
                print(f"Server handshake successful")
                session = Session(sock,addr,fernet_key,threading.current_thread)
                if callback:
                    callback(session)
            else:
                print(f"Server handshake failed")
        except Exception as e:
            print(f"Error handling client {addr}: {e}")