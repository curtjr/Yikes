from portal.transport import Client
from portal.transport import Server
from portal.commands import CommandExecutor

def connect(host):
    transport = Client(host)
    return transport

def start_server(callback):
    transport = Server(callback)
    return transport