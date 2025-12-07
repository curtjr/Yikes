from yikes.transport import Transport

"'CLIENT'"
class Client():
    """
    Client class used for connecting to a server.
    To create a client please use the create_client() function!
    """
    def __init__(self, addr:tuple):
        super().__init__()  
        self.addr = addr
        self.transport = Transport(addr)
        self.listeners = {}

    def connect(self):
        "'Establish connection to the server via transport and preform a handshake'"
        self.transport.connect()
        self.transport.start_client()

    def send_bytes(self, bytes:bytes):
        "'Sends bytes to the connected server'"
        self.transport.send_bytes(bytes)

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