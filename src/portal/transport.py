import socket
import json
import select

from portal.auth import Authenticator

port = 22
host = "0.0.0.0"
max_connections = 10

class SocketHandler:
    def send_message(self, message_dict):
        raw = json.dumps(message_dict).encode()
        self.sock.sendall(raw)

    def receive_message(self, timeout=0.1):
        ready, _, _ = select.select([self.sock], [], [], timeout)
        if not ready:
            return None
        data = b""
        try:
            chunk = self.sock.recv(4096)
            if chunk:
                data += chunk
        except BlockingIOError:
            pass
        return data.decode("utf-8", errors="ignore")

class Client(SocketHandler):
    def __init__(self, host, port):
        super().__init__()  
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        # Prepare authenticator with your credential store
        self.auth = Authenticator()

    def authenticate(self, username: str, password: str):
        # Sends credentials and waits for server approval.
        return self.auth.client_handshake(self, username, password)

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

        print(f"Server listening on {host}:{port}")

    def run(self):
        """Main loop: accept connections, authenticate, then hand off."""
        try:
            while True:
                conn, addr = self.server.accept()
                print(f"Connection from {addr}")

                # Swap in the client socket for I/O
                self.sock = conn

                # Run the auth handshake over that socket
                if self.auth.server_handshake(self):
                    print(f"Client {addr} authenticated successfully.")
                    if self.on_client_connect:
                        self.on_client_connect(conn, addr)
                else:
                    print(f"Client {addr} failed authentication.")

                conn.close()
        finally:
            self.server.close()



        

