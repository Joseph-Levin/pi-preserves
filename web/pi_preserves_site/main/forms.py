from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as auth_user
from django.forms import widgets

from . import models


def must_be_unique(value):
  user_objects = auth_user.objects.filter(email=value)
  if len(user_objects) > 0:
    raise forms.ValidationError("Email already in use")
  return value


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


class FolderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
      self.userid = kwargs.pop('userid', None)
      kwargs.update(initial={'owner': self.userid})
      super(FolderForm, self).__init__(*args, **kwargs)
      self.fields['parent_folder'].queryset = models.Folder.objects.filter(owner=self.userid)

    class Meta:
      model = models.Folder
      fields = '__all__'
      widgets = {
        'owner': forms.HiddenInput(),
        'files': forms.HiddenInput(),
        'sub_folders': forms.HiddenInput(),
      }


class FileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
      # instance = kwargs.get('instance', None)
      self.userid = kwargs.pop('userid', None)
      kwargs.update(initial={'author': self.userid})
      super(FileForm, self).__init__(*args, **kwargs)
      self.fields['shared_to'].queryset = auth_user.objects.exclude(pk=self.userid)#.exclude(shared_files__id=)
      self.fields['parent_folder'].queryset = models.Folder.objects.filter(owner=self.userid)

    class Meta:
      model = models.File
      fields = ('description', 'file', 'author', 'shared_to', 'public', 'parent_folder')
      widgets = {
        'author': forms.HiddenInput(),
      }

    def save(self, commit=True):
        file = super(FileForm, self).save(commit=False)
        file.size = file.file.size
        file.shared_to.add(*self.cleaned_data['shared_to'])
        if commit:
            file.save()
        return file

class EditFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
      self.userid = kwargs.pop('userid', None)
      super(EditFileForm, self).__init__(*args, **kwargs)
      self.fields['shared_to'].queryset = auth_user.objects.exclude(pk=self.userid)#.exclude(shared_files__id=)
      self.fields['parent_folder'].queryset = models.Folder.objects.filter(owner=self.userid)

    class Meta:
      model = models.File
      fields = ('description', 'author', 'shared_to', 'public', 'parent_folder')
      widgets = {
        'author': forms.HiddenInput(),
      }

    def save(self, commit=True):
        file = super(EditFileForm, self).save(commit=False)
        file.size = file.file.size
        file.shared_to.add(*self.cleaned_data['shared_to'])
        if commit:
            file.save()
        return file
