from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import File
from .forms import RegistrationForm, UploadForm#, CreateNewFile
from .fileupload import FileUploadToServer


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
            form.save(request)
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


def index(request, id):
    f = File.objects.get(id=id)
    if f in request.user.file.all():
        return render(request, "main/file.html", {"file":f})
    
    return render(request, "main/file.html", {})


@method_decorator(csrf_exempt, 'dispatch')
def upload_files(request):
    request.upload_handlers.insert(0, FileUploadToServer())
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.author = request.user
            file.save()
            # form.save()
            # request.user.file.add(form.File)

        return HttpResponseRedirect('/%i' %file.id)

    else:
        form = UploadForm()

    return render(request, 'main/upload.html', {'form':form})


def view_files(request):
    return render(request, "main/view_files.html", {})


# def download_file(request):
