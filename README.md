# Yikes

## What is Yikes?

Yikes is a *transmission control protocol* **(TCP)** used for sending info **securely** across the internet or local subnets. Yikes is meant to be an easy-to-use alternative to other, more complex, 
SSH/tunneling protocols. Yikes uses cryptography to create a secure RSA handshake with a Fernet key for two-way security. Once a handshake 
is complete anything can be sent via bytes from server to client or client to server until the client or server disconnects.

## How do you use Yikes?

Once the package has been downloaded manually, or pip installed, using the package is as simple as:

```python
# Server side

server = Yikes.Server() 
server.start_server(('0.0.0.0',8000)'
```

```python
# Client side

client = Yikes.Client()
client.connect('0.0.0.0',8000)
```
