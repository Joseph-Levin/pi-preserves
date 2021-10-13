import socket

host = '127.0.0.1'
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((host, port))

s.listen(1)

conn, addr = s.accept()

print("Connection from:", str(addr))

message = conn.recv(1024)
print(message)

conn.close()
