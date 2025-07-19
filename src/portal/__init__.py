from portal.transport import Client, Server
import threading

def create_client(host: str, port=22, callback=None):
    transport = Client(host, port, callback)
    thread = threading.Thread(target=transport.run_client, daemon=False)
    thread.start()
    return transport, thread

def create_server(host: str, port=22, callback=None):
    transport = Server(host,port,callback)
    thread = threading.Thread(target=transport.run_server, daemon=False)
    thread.start()
    return transport, thread