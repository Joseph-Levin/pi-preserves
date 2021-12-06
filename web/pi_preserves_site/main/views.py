from django.db import reset_queries
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from socket import socket, AF_INET, SOCK_STREAM
from django.conf import settings
from django.db.models import Q

from pathlib import Path
from string import ascii_uppercase, digits
from random import choice
from datetime import date, datetime
from hashlib import md5
from os.path import exists

from .models import File, Folder
from .forms import RegistrationForm, FileForm, FolderForm#, CreateNewFile
from .fileupload import FileUploadToServer, recv_ack, send_ack, BUFFER_SIZE
from .exceptions import FileServerError

FILE_EXTENSIONS = {
    'image': ['.apng', '.avif', '.gif', '.jpg', '.jpeg', '.jfif', '.pjpeg', '.pgp', '.png', '.svg', '.webp'],
    'audio': ['.mp3', '.mpeg', '.wav'],
    'video': ['.mp4', '.ogg', '.webm'],
    'pdf': ['.pdf'],
}

def temp_name_generator(size=4, chars=ascii_uppercase + digits):
    now = datetime.now().strftime('%m-%d-') 

    return now + ''.join(choice(chars) for _ in range(size))

def home(request):
    context = {
        "title": "Pi Preserves",
        "body": "Pi Preserves is a work in progress",
    }

    return render(request, "main/home.html", context=context)


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            # insert root folder creation
            Folder.objects.create(name='Home', owner=user)
            return redirect('/login/')

    else:
        form = RegistrationForm() 

    context = {
        'title': 'Registration Page',
        'form': form,
    }

    return render(request, 'registration/register.html', context=context)


def logout_view(request):
    logout(request)
    return redirect('/login/')


def download_file_request(request, id):
    file_obj = File.objects.get(id=id)
    filename = file_obj.file.name

    extension = file_obj.file.name.rsplit('.')[-1].lower()
    cached_path = Path.joinpath(settings.MEDIA_ROOT, 'temp', file_obj.hash + '.' + extension)
    
    if not exists(cached_path):
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
            file += data
            data = sock.recv(BUFFER_SIZE)
            send_ack(sock)
        sock.close()
        response = HttpResponse(bytes(file))

    else:
        response = HttpResponse(open(cached_path, mode='rb').read())
    
    response['Content-Disposition'] = 'inline; filename=' + filename.split('/')[-1]
    return response



@login_required
@method_decorator(csrf_exempt, 'dispatch')
def upload_files(request):
    #request.upload_handlers.insert(0, FileUploadToServer())
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES, userid=request.user.id)
        if form.is_valid():
            form.save(request)
            return HttpResponseRedirect('/')

    else:
        form = FileForm(userid=request.user.id)

    return render(request, 'main/upload.html', {'form':form})


@login_required
def delete_file(request, id):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((settings.FILE_SERVER_ADDRESS, settings.FILE_SERVER_PORT)) 
    sock.send("delete".encode())
    if recv_ack(sock) == False:
        raise FileServerError("Server did not successfully respond")
    
    file = File.objects.get(id=id)
    sock.send(file.file.name.encode())

    if recv_ack(sock) == False:
        raise FileServerError("Server did not successfully respond")

    if recv_ack(sock) == False:
        raise FileServerError("File not deleted successfully")
    
    file.delete()

    return render(request, "main/view_files.html", {})


def view_files(request, sort_method="newest", filter_method="owned"):
    # if sort_method == "ascending":
    #     files = File.objects.filter(author=request.user).order_by('file__name')
    # elif sort_method == "descending":
    #     files = File.objects.filter(author=request.user).order_by('-file__name')
    # elif sort_method == "oldest":
    Q_obj = Q()

    if filter_method == "shared":
        Q_obj = Q(shared_to__id=request.user.id)

    elif filter_method == "all_files":
        Q_obj = Q(public=True) | Q(shared_to__id=request.user.id) | Q(author=request.user)

    elif filter_method == "public":
        Q_obj = Q(public=True)

    else:
        Q_obj = Q(author=request.user)


    if sort_method == "oldest":
        files = File.objects.filter(Q_obj).order_by('-uploaded_at')
    else:
        files = File.objects.filter(Q_obj).order_by('uploaded_at')

    default_icon = settings.MEDIA_URL + 'default_file.png'
    music_icon = settings.MEDIA_URL + 'music_icon.png'

    context = {
        'files': files,
        'default_icon': default_icon,
        'music_icon': music_icon,
        'file_extensions': FILE_EXTENSIONS,
        'sort_method': sort_method,
        'filter_method': filter_method,
    }

    return render(request, "main/view_files.html", context=context)


@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST, userid=request.user.id)
        if form.is_valid():
            form.save(request)
            return redirect('/')
    
    else:
        form = FolderForm(userid=request.user.id)

    context = {
        'form': form,
    }

    return render(request, 'main/create_folder.html', context=context)


def view_file(request, id):
    Fobj = File.objects.get(id=id)
    shared_to = Fobj.shared_to

    date_published = Fobj.uploaded_at.strftime('%B %-d, %Y')
    
    default_icon = settings.MEDIA_URL + 'default_file.png'

    context = {
        'fobj': Fobj,
        'file_extensions': FILE_EXTENSIONS,
        'date': date_published,
        'default_icon': default_icon,
    }

    return render(request, 'main/view_file.html', context=context)
