# Yikes

## What is Yikes?

Yikes is a *transmission control protocol* **(TCP)** used for sending info **securely** across the internet or local subnets. 
Yikes uses cryptography to create a secure RSA handshake with a Fernet key for two-way security. Once the handshake 
is complete anything can be sent via bytes from server to client or client to server until the client or server disconnects.

## What can Yikes be used for?

Yikes is meant to be an easy-to-use alternative to other, more complex, SSH/tunneling protocols. It can be used for anything related
to sending information from computer to computer. Some examples are small online games, security applications, or a social media platform.
Yikes is in no way optimized for any specific application, though some optimizations may be added in the future to accomodate users.

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
