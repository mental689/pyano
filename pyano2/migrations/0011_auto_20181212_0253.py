# Generated by Django 2.1.2 on 2018-12-12 02:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_auto_20181208_1426'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pyano2', '0010_auto_20181209_1230'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frame', models.IntegerField()),
                ('value', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VATICAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VATICBox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xtl', models.IntegerField()),
                ('ytl', models.IntegerField()),
                ('xbr', models.IntegerField()),
                ('ybr', models.IntegerField()),
                ('frame', models.IntegerField()),
                ('occluded', models.BooleanField(default=False)),
                ('outside', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VATICBoxAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes2boxes', to='pyano2.VATICBox')),
                ('box', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boxes2attributes', to='pyano2.VATICBox')),
            ],
        ),
        migrations.CreateModel(
            name='VATICJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('istraining', models.BooleanField(default=False, help_text='Is this job for training?')),
                ('completed', models.BooleanField(default=False, help_text='Is the job completed?')),
                ('paid', models.BooleanField(default=False, help_text='Is the annotator paid?')),
                ('published', models.BooleanField(default=False, help_text='Is this published?')),
                ('status', models.IntegerField(choices=[(0, 'Not decided'), (1, 'Accepted'), (2, 'Rejected')], default=0, help_text='Status')),
                ('bonus', models.FloatField(default=0, help_text='Bonus')),
                ('uuid', models.CharField(help_text='UUID', max_length=255, unique=True, verbose_name='Job unique identifier')),
                ('training_overlap', models.FloatField(default=0.25)),
                ('training_tolerance', models.FloatField(default=0.2)),
                ('training_mistakes', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VATICJobGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=250)),
                ('duration', models.IntegerField()),
                ('keywords', models.CharField(max_length=250)),
                ('height', models.IntegerField(default=650)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VATICLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VATICPath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paths', to='pyano2.VATICJob')),
                ('label', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paths', to='pyano2.VATICLabel')),
            ],
        ),
        migrations.CreateModel(
            name='VATICSegment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.IntegerField()),
                ('stop', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VATICTrainingOf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VATICVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=250)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('totalframes', models.IntegerField()),
                ('location', models.CharField(max_length=250)),
                ('skip', models.IntegerField(default=0)),
                ('perobjectbonus', models.FloatField(default=0)),
                ('completionbonus', models.FloatField(default=0)),
                ('isfortraining', models.BooleanField(default=False)),
                ('blowradius', models.IntegerField(default=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pyano_video', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vaticvideos', to='survey.Video')),
            ],
        ),
        migrations.CreateModel(
            name='VATICWorkerJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job2workers', to='pyano2.VATICJob')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worker2jobs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='credit',
            name='survey',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='points', to='survey.Survey'),
        ),
        migrations.AddField(
            model_name='vatictrainingof',
            name='video_test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='testvideos', to='pyano2.VATICVideo'),
        ),
        migrations.AddField(
            model_name='vatictrainingof',
            name='video_train',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trainvideos', to='pyano2.VATICVideo'),
        ),
        migrations.AddField(
            model_name='vaticsegment',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='segments', to='pyano2.VATICVideo'),
        ),
        migrations.AddField(
            model_name='vaticlabel',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labels', to='pyano2.VATICVideo'),
        ),
        migrations.AddField(
            model_name='vaticjobgroup',
            name='cost',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobgroups', to='pyano2.Credit'),
        ),
        migrations.AddField(
            model_name='vaticjob',
            name='group',
            field=models.ForeignKey(help_text='Group', on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='pyano2.VATICJobGroup'),
        ),
        migrations.AddField(
            model_name='vaticjob',
            name='segment',
            field=models.ForeignKey(help_text='Segment', on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='pyano2.VATICSegment'),
        ),
        migrations.AddField(
            model_name='vaticbox',
            name='path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boxes', to='pyano2.VATICPath'),
        ),
        migrations.AddField(
            model_name='vaticattribute',
            name='label',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='pyano2.VATICLabel'),
        ),
        migrations.AddField(
            model_name='attributeannotation',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pyano2.VATICAttribute'),
        ),
        migrations.AddField(
            model_name='attributeannotation',
            name='path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='pyano2.VATICPath'),
        ),
    ]
