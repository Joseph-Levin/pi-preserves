# Generated by Django 3.2.7 on 2021-09-30 02:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_file_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='user',
            new_name='author',
        ),
    ]
