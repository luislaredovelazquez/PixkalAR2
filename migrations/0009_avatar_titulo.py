# Generated by Django 3.0.5 on 2020-05-20 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pixkal2', '0008_remove_busqueda_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='avatar',
            name='titulo',
            field=models.CharField(default='Avatar', max_length=100),
        ),
    ]
