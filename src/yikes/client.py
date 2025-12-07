from yikes.transport import Transport

"'CLIENT'"
class Client():
    """
    Client class used for connecting to a server.
    To create a client please use the create_client() function!
    """
    def __init__(self):
        super().__init__()  
        self.addr = None
        self.transport = Transport("c")
        self.listeners = []

    def connect(self, addr):
        "'Establish connection to the server and preform security handshake'"
        self.addr = addr
        self.transport.start_client(addr)

    def close_sock(self, sock):
        """
        Closes the provided socket.
        
        Args:
            sock(socket.socket): The socket you want to close.
        """
        sock.close()

    def send_bytes(self, data:bytes):
        "'Sends bytes to the connected server'"
        self.transport.send_bytes(data)

    def recv_bytes(self) -> bytes:
        "'Receives bytes from the connected server'"
        return self.transport.recv_bytes()
    
    def add_connection_listener(self, callback):
        """
        Adds a listener function that will be called whenever a new client connects to the server.
        
        Args:
            callback(function): The function to be called on new connection
        """
        self.transport.listeners.append(callback)