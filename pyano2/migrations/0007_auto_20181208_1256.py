# Generated by Django 2.1.2 on 2018-12-08 12:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pyano2', '0006_auto_20181208_0556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyword',
            name='topic',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='pyano2.Topic'),
        ),
        migrations.AlterField(
            model_name='keyword',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='searchresult',
            name='keyword',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='searches', to='pyano2.Keyword'),
        ),
    ]