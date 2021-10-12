import socket

host = '127.0.0.1'
port = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((host, port))

sock.send(b"Hello from python")
sock.close()
