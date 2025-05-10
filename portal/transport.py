import socket

port = 24

class Client:
    def __init__(self, host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

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
    
class Server:
    def __init__(self, host="0.0.0.0"):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(10)  # Allow up to 10 connections
        print(f"Server listening on port {port}...")

    def run(self):
        while True:
            conn, addr = self.server.accept()
            print(f"Connection from {addr}")
            data = conn.recv(1024).decode()
            print(f"Received: {data}")
            conn.send("Hello, Client!".encode())  # Send response
            conn.close()

