# Generated by Django 2.1.2 on 2018-12-09 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
        ('pyano2', '0007_auto_20181208_1256'),
    ]

    operations = [
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.FloatField(default=1.0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('survey', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='points', to='survey.Survey', unique=True)),
            ],
        ),
    ]