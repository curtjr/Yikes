from yikes.transport import Transport
import socket

"'SERVER'"
class Server():
    """
    Server class used for accepting client connections.
    To create a server please use the create_server() function!
    """
    def __init__(self):
        super().__init__()  

        self.max_connections = 0  # Default max connections

        self.transport = Transport("s")

    def start_server(self, addr):
        """
        Creates a server and binds it to the address provided during initialization.
        The server will start listening for incoming client connections. Whenever a client connects, 
        they preform a handshake with the server and any functions provided as listeners using the 
        add_connection_listener() method will be called.
        """
        self.transport.start_server(addr)
        
    def close_sock(self, sock:socket.socket):
        """
        Closes the provided socket.
        
        Args:
            sock(socket.socket): The socket you want to close.
        """
        sock.close()

    def get_connections(self):
        """
        Returns a dictionary of client sessions that are currently connected to the server.

        Returns:
            Dict[Addr]: A dictionary containing:
                - The socket of the respective client address accessible with the key "socket"
                - The fernet key of the respective client address accessible with the key "fernet_key"
        """
        return self.transport.connections

    def set_max_connections(self, max_connections):
        """
        Sets the maximum number of clients allowed to connect to the server. Set to 0 if you want the maximum
        number of connections to be capped by your kernel. If the current number 
        of connections is equal to or above the maximum no new connection attempts will be accepted.
        
        Args:
            max_connections(int): Maximum number of connections
        """
        self.max_connections = max_connections

    def add_connection_listener(self, callback):
        """
        Adds a listener function that will be called whenever a new client connects to the server.
        The callback when called is given two arguments: the socket and address of the connecting client, respectively.
        
        Args:
            callback(function): The function to be called on new connection
        """
        self.transport.listeners.append(callback)

    def send_bytes(self, data:bytes, addr):
        "'Sends bytes to the connected server'"
        self.transport.send_bytes(data, addr)

    def recv_bytes(self, addr) -> bytes:
        "'Receives bytes from the connected server'"
        return self.transport.recv_bytes(addr)