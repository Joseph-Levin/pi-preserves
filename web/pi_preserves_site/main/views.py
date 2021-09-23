from django.shortcuts import render
from django.http import HttpResponse

from .models import File
from .forms import CreateNewFile

def home(request):
    context = {
        "title": "Pi Preserves",
        "body": "Poodog",
    }

    return render(request, "main/home.html", context=context)

def create(request):
    if request.method == "POST":
        form = CreateNewFile(request.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            s = form.cleaned_data["size"]
            f = File(name=n, size=s)
            f.save()

        return HttpResponse(f)

    else:
        form = CreateNewFile()

    context = {
        "form": form,
    }
    return render(request, "main/create.html", context=context)