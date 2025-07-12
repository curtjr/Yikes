from portal.transport import Client, Server
from portal.auth import Authenticator

def create_client(host, port, auth_store):
    transport = Client(host, port, auth_store)
    return transport

def create_server(auth_data,callback):
    transport = Server(auth_data,callback)
    return transport