# Generated by Django 2.2.1 on 2019-06-10 08:12

from django.db import migrations, models
import garbage.models


class Migration(migrations.Migration):

    dependencies = [
        ('garbage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='garbageimage',
            name='photo',
            field=models.ImageField(upload_to=garbage.models.upload_image_to),
        ),
    ]
