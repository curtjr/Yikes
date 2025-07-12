from portal.transport import Client, Server
from portal.auth import Authenticator

def create_client(host: str, port: int):
    transport = Client(host, port)
    return transport

def create_server(auth_store: dict[str,str],callback):
    transport = Server(auth_store,callback)
    return transport