# Generated by Django 2.1.2 on 2018-12-07 17:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pyano2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='invited',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitees', to=settings.AUTH_USER_MODEL),
        ),
    ]
