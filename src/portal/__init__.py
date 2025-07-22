from portal.transport import Client, Server, Session
import threading

def create_client(host: str, port=22, callback=None):
    """
    Creates a client used for connecting to a server.
    
    Args:
        host(str): Ip of the server.
        port(int): Port your server is listening on.
        callback(function): Function that executes after the client successfully connects to the server.

    Returns:
        class: Client class.
    """
    transport = Client(host, port, callback)
    thread = threading.Thread(target=transport.run_client, daemon=False)
    thread.start()
    return transport, thread

def create_server(host: str, port=22, callback=None):
    """
    Creates a server.
    
    Args:
        host(str): Ip of the server.
        port(int): Port your server is listening on.
        callback(function): Function that executes after a client successfully connects to the server.

    Returns:
        class: Server class.
    """
    transport = Server(host,port,callback)
    thread = threading.Thread(target=transport.run_server, daemon=False)
    thread.start()
    return transport, thread