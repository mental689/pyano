# Generated by Django 2.1.2 on 2018-12-12 18:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyano2', '0013_vaticbid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vaticjob',
            name='status',
        ),
    ]