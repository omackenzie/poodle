# Generated by Django 4.1 on 2024-04-28 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='document',
            field=models.FileField(upload_to='submissions'),
        ),
    ]
