from portal.transport import Client, Server

def create_client(host: str, port=22):
    transport = Client(host, port)
    return transport

def create_server(host: str, port=22, callback=None):
    transport = Server(host,port,callback)
    return transport