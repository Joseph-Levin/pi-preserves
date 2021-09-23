from django import forms

class CreateNewFile(forms.Form):
    name = forms.CharField(label="File Name", max_length=255)
    size = forms.IntegerField(label="File Size")