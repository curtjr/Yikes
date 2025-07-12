import json
import jwt

class Authenticator:
    def __init__(self, auth_data):
        self.auth_data = auth_data
        
    def client_handshake(self, transport, username, password):
        transport.send_message({"type": "auth", "username": username, "password": password})
        while True:
            msg = transport.receive_message()
            if msg and msg.get("type") == "auth":
                return msg.get("status") == "success"

    def server_handshake(self, transport):
        while True:
            msg = transport.receive_message()
            if msg and msg.get("type") == "auth":
                user, pw = msg["username"], msg["password"]
                ok = self.auth_store.get(user) == pw
                transport.send_message({"type": "auth", "status": "success" if ok else "failed"})
                return ok

class StaticTokenAuthenticator:
    def __init__(self, valid_tokens):
        self.valid_tokens = set(valid_tokens)

    def client_handshake(self, transport, token):
        transport.send_message({"type": "token", "token": token})
        while True:
            msg = transport.receive_message()
            if not msg:
                continue
            if msg.get("type") != "token":
                continue
            return msg.get("status") == "success"

    def server_handshake(self, transport):
        while True:
            msg = transport.receive_message()
            if not msg:
                continue
            if msg.get("type") != "token":
                continue

            presented = msg.get("token")
            ok = presented in self.valid_tokens
            status = "success" if ok else "failed"
            transport.send_message({"type": "token", "status": status})
            return ok
    