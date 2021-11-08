import os
import socket
import pathlib
from urllib.parse import urljoin
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils._os import safe_join
from django.utils.encoding import filepath_to_uri
from django.utils.functional import cached_property
from django.conf import settings
from .fileupload import recv_ack, send_ack, BUFFER_SIZE
from .exceptions import FileServerError

class PiStorage(Storage):
  def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL,
    file_permissions_mode=None, directory_permissions_mode=None):
    self._location = location
    self._base_url = base_url
    self._file_permissions_mode = file_permissions_mode
    self._directory_permissions_mode = directory_permissions_mode

  def _value_or_setting(self, value, setting):
      return setting if value is None else value

  @cached_property
  def base_location(self):
      return self._value_or_setting(self._location, settings.MEDIA_ROOT)

  @cached_property
  def location(self):
      return os.path.abspath(self.base_location)

  @cached_property
  def base_url(self):
      if self._base_url is not None and not self._base_url.endswith('/'):
          self._base_url += '/'
      return self._value_or_setting(self._base_url, settings.MEDIA_URL)

  @cached_property
  def file_permissions_mode(self):
      return self._value_or_setting(self._file_permissions_mode, settings.FILE_UPLOAD_PERMISSIONS)

  @cached_property
  def directory_permissions_mode(self):
      return self._value_or_setting(self._directory_permissions_mode, settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS)

  def _open(self, filename, mode='rb'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((settings.FILE_SERVER_PORT, settings.FILE_SERVER_ADDRESS))
    s.send("download".encode())
    if recv_ack(s) == False:
      raise FileServerError("Server did not successfully respond")

    s.send(filename.encode())
    if recv_ack(s) == False:
      raise FileServerError("Server did not successfully respond")

    file_data = ''
    data = s.recv(BUFFER_SIZE)
    send_ack(s)
    while data:
      file_data += data
      data = s.recv(BUFFER_SIZE)
      send_ack(s)
    s.close()

    return ContentFile(file_data, filename)

  def _save(self, name, content):
    full_path = self.path(name)
    # Create any intermediate directories that do not exist.
    # directory = os.path.dirname(full_path)
    # try:
    #     if self.directory_permissions_mode is not None:
    #         # Set the umask because os.makedirs() doesn't apply the "mode"
    #         # argument to intermediate-level directories.
    #         old_umask = os.umask(0o777 & ~self.directory_permissions_mode)
    #         try:
    #             os.makedirs(directory, self.directory_permissions_mode, exist_ok=True)
    #         finally:
    #             os.umask(old_umask)
    #     else:
    #         os.makedirs(directory, exist_ok=True)
    # except FileExistsError:
    #     raise FileExistsError('%s exists and is not a directory.' % directory)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((settings.FILE_SERVER_ADDRESS, settings.FILE_SERVER_PORT))
    s.send("upload".encode())
    if recv_ack(s) == False:
      raise FileServerError("Server did not successfully respond")
    s.send(name.encode())
    if recv_ack(s) == False:
      raise FileServerError("Server did not successfully respond")

    # for chunk in content.chunks():
    #   s.send(chunk)
    #   if recv_ack(s) == False:
    #     raise FileServerError("Server did not successfully respond")
    while True:
      bytes_read = content.read(BUFFER_SIZE)
      if not bytes_read:
        break
      s.send(bytes_read)
      if recv_ack(s) == False:
        raise FileServerError("Server did not successfully respond")

    
    s.close()

    return name



  
  def path(self, name):
    return safe_join(self.location, name)
  
  #TODO make new server action to check if file exists
  def exists(self, name):
    return False

  def url(self, name):
    if self.base_url is None:
      raise ValueError("This file is not accessible via a URL")
    url = filepath_to_uri(name)
    if url is not None:
      url = url.lstrip('/')
    return urljoin(self.base_url, url)
