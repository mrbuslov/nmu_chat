# Generated by Django 3.2.6 on 2022-02-07 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to='uploaded_files/files/'),
        ),
    ]
