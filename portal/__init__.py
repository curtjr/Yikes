from portal.transport import Transport
from portal.commands import CommandExecutor

def connect(host):
    transport = Transport(host)
    return CommandExecutor(transport)