from django import template
from django.template.defaultfilters import stringfilter
from hashlib import md5
from os.path import exists
from pathlib import Path
from django.conf import settings
from socket import socket, AF_INET, SOCK_STREAM
from ..fileupload import recv_ack, send_ack, BUFFER_SIZE

register = template.Library()

@register.filter
@stringfilter
def filenamesplit(value):
    """Converts a filepath to only the filename"""
    return value.split('/')[-1]

@register.filter
def preview_path_hash(fobj):
    
    filename = fobj.file.name
    extension = fobj.extension
    hash = fobj.hash
    temp_path = Path.joinpath(settings.MEDIA_ROOT, 'temp', hash + extension)

    if not exists(temp_path):
        new_hash = md5()
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((settings.FILE_SERVER_ADDRESS, settings.FILE_SERVER_PORT))
        sock.send("download".encode())
        recv_ack(sock)


        sock.send(filename.encode())
        recv_ack(sock)

        file = bytearray()
        data = sock.recv(BUFFER_SIZE)
        send_ack(sock)
        while data:
            new_hash.update(data)
            file += data
            data = sock.recv(BUFFER_SIZE)
            send_ack(sock)
        sock.close()

        fobj.hash = new_hash.hexdigest()
        fobj.save()
        temp_name = new_hash.hexdigest() + extension
        f = open(Path.joinpath(settings.MEDIA_ROOT, 'temp', temp_name), mode='wb')
        f.write(file)
        f.close()
        
        preview_path = settings.MEDIA_URL + 'temp/' + temp_name

    else:
        preview_path = settings.MEDIA_URL + 'temp/' + hash + extension
    
    return preview_path