# Generated by Django 3.0.5 on 2020-06-17 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pixkal2', '0002_dash_id_actividad'),
    ]

    operations = [
        migrations.AddField(
            model_name='dash',
            name='estado',
            field=models.CharField(choices=[('I', 'Inactivo'), ('C', 'Cancelado'), ('A', 'Activo'), ('T', 'Terminado')], default='A', max_length=1),
        ),
    ]
