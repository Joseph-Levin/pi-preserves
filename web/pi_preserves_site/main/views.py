from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from socket import socket, AF_INET, SOCK_STREAM
from django.conf import settings

from .models import File, Folder
from .forms import RegistrationForm, FileForm, FolderForm#, CreateNewFile
from .fileupload import FileUploadToServer, recv_ack, send_ack, BUFFER_SIZE
from .exceptions import FileServerError


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
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((settings.FILE_SERVER_ADDRESS, settings.FILE_SERVER_PORT))
    sock.send("download".encode())
    recv_ack(sock)


    filename = File.objects.get(id=id).file.name
    print(filename)
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


def view_files(request):
    return render(request, "main/view_files.html", {})


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
    file = File.objects.get(id=id)
    shared_to = file.shared_to
    print(shared_to)

    context = {
        'file': file,
    }

    return render(request, 'main/view_file.html', context=context)
