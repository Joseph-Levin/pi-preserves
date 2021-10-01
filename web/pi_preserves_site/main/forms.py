from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as auth_user

from . import models


def must_be_unique(value):
  user_objects = auth_user.objects.filter(email=value)
  if len(user_objects) > 0:
    raise forms.ValidationError("Email already in use")
  return value


# class CreateNewFile(forms.Form):
#     name = forms.CharField(label="File Name", max_length=255)
#     size = forms.IntegerField(label="File Size")

class UploadForm(forms.ModelForm):
  class Meta:
    model = models.File
    fields = ('description', 'file',)

# class UploadForm(forms.Form):
#   title = forms.CharField(max_length=255)
#   file_field = forms.FileField()
    

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        validators=[must_be_unique]
        )

    class Meta:
        model = auth_user
        fields = (
          "username",
          "email",
          "password1",
          "password2",
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user