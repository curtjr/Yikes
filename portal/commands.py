class CommandExecutor:
    def __init__(self, transport):
        self.transport = transport
    
    def run_command(self, command):
        self.transport.send_data(command)
        return self.transport.receive_data()