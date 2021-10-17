import os
import socket
from sys import argv

BUFFER_SIZE = 2048
ACK = b"ACK\x00"
ACK_SIZE = 16
FAILURE = b"/--FAILURE--/\x00"
host = '127.0.0.1'
port = 8888

def send_ack(s):
  s.send("ACK".encode())
  return

def recv_ack(s):
  ack = s.recv(ACK_SIZE)
  if ack == ACK:
    return
  elif ack == FAILURE:
    print("Failure detected")
    exit()
  else:
    print("ACK not received. Received", ack)
    exit()


filename = argv[1]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"- Connecting to {host}:{port}")
sock.connect((host, port))
if argv[2] == "upload":
  sock.send("upload".encode())
  recv_ack(sock)

  sock.send(filename.encode())
  recv_ack(sock)

  with open(filename, "rb") as f:
    while True:
      bytes_read = f.read(BUFFER_SIZE)
      if not bytes_read:
        break
      sock.send(bytes_read)
      recv_ack(sock)

elif argv[2] == "download":
  sock.send("download".encode())
  recv_ack(sock)

  sock.send(filename.encode())
  recv_ack(sock)

  with open(filename, "wb") as f:
    data = sock.recv(BUFFER_SIZE)
    send_ack(sock)
    while data:
      f.write(data)
      data = sock.recv(BUFFER_SIZE)
      send_ack(sock)
    


sock.close()
