# Generated by Django 2.1.2 on 2018-12-12 15:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pyano2', '0012_vaticjob_ready'),
    ]

    operations = [
        migrations.CreateModel(
            name='VATICBid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approved_bids', to=settings.AUTH_USER_MODEL)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='pyano2.VATICJob')),
            ],
        ),
    ]