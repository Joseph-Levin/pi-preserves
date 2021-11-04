from django.core.files.uploadhandler import FileUploadHandler, TemporaryFileUploadHandler
from django.core.files.uploadedfile import TemporaryUploadedFile
from io import BytesIO
from socket import socket, AF_INET, SOCK_STREAM
from django.conf import settings


BUFFER_SIZE = 2048
ACK = b"ACK\x00"
ACK_SIZE = 4
FAILURE = b"FAL\x00"

def send_ack(s):
  s.send("ACK".encode())
  return

def recv_ack(s):
  ack = s.recv(ACK_SIZE)
  if ack == ACK:
    return True
  elif ack == FAILURE:
    print("Failure detected")
    return False
  else:
    print("ACK not received. Received", ack)
    return False

class FileUploadToServer(TemporaryFileUploadHandler):
  
  # Create new file and socket to transfer file
  def new_file(self, *args, **kwargs):
    super().new_file(*args, **kwargs)
    self.file = TemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset, self.content_type_extra)
    print("Content Type", self.content_type)
    print("Charset", self.charset)
    print("Extra content", self.content_type_extra)
    print("Content length", self.content_length)

  def receive_data_chunk(self, raw_data, start):
      self.file.write(raw_data)
      return None

# TODO error checking for recv_ack
  def file_complete(self, file_size):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((settings.FILE_SERVER_ADDRESS, settings.FILE_SERVER_PORT))
    sock.send("upload".encode())
    recv_ack(sock)
    sock.send(self.file_name.encode())
    recv_ack(sock)

    self.file.seek(0)
    self.file.size = file_size
    while True:
      bytes_read = self.file.read(BUFFER_SIZE)
      if not bytes_read:
        break
      sock.send(bytes_read)
      recv_ack(sock)
    
    sock.close()

    self.file.seek(0)
    return self.file