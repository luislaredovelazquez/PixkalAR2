# Generated by Django 3.0.5 on 2020-06-17 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pixkal2', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dash',
            name='id_actividad',
            field=models.IntegerField(default=0),
        ),
    ]
