# Generated by Django 3.0.5 on 2020-06-05 00:32

from django.db import migrations, models
import pixkal2.models


class Migration(migrations.Migration):

    dependencies = [
        ('pixkal2', '0012_perfil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfil',
            name='imagen_busqueda',
            field=models.ImageField(upload_to=pixkal2.models.upload_location),
        ),
    ]