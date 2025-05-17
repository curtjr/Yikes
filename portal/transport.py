import socket
import json

port = 139
host = "0.0.0.0"
max_connections = 10

class Client:
    def __init__(self, host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def get_socket(self):
        return self.sock

    def authenticate(self,username,password):
        data = {
             "type": "auth",
             "username": username,
             "password": password,
        }
        self.send_data(data)
        authenticated = False
        while self.sock.recv(1, socket.MSG_PEEK) and not authenticated:
            new_data = self.receive_data()
            if new_data:
                message = json.loads(new_data)
                if message["type"] == "auth":
                    if message["status"] == "success":
                        authenticated = True
                        return True

    def send_data(self, data):
        self.sock.send(data.encode())

    def receive_data(self):
        buffer = b""
        while True:
            chunk = self.sock.recv(1024)
            if not chunk:  # Stop when no more data is received
                break
            buffer += chunk
        return buffer.decode()
    
def check_auth(username, password, auth):
    clients = json.loads(auth)
    for client in clients['clients']:
        if client['username'] == username and client['password'] == password:
            return True
    return False

class Server:
    def __init__(self,auth,on_client_connect=None):
        self.on_client_connect = on_client_connect
        self.auth = json.loads(auth)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(max_connections)  # Allow up to 10 connections
        print(f"Server listening on port {port}...")

    def run(self):
        while True:
            conn, addr = self.server.accept()
            print(f"Connection from {addr}")
            socket = conn
            while socket.recv(1, socket.MSG_PEEK) and not authenticated:
                try:
                    data = socket.recv(1024).decode().strip()
                    if not data:
                        break
                    message = json.loads(data)
                    if message['type'] == 'auth':
                        result = check_auth(message['username'], message['password'],self.auth)
                        if result:
                            result_data={
                                "type": "auth",
                                "status": "success",
                            }
                            socket.send(result_data.encode())
                            authenticated = True
                        else:
                            socket.send("failed".encode())
                            socket.close()
                            break
                except Exception as e:
                    print(f"Error: {e}")
                    break

            # Notify the external script
            if self.on_client_connect:
                self.on_client_connect(conn, addr)

            conn.close()

        

