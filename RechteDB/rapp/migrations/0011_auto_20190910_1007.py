# Generated by Django 2.2.1 on 2019-09-10 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0010_auto_20190909_1204'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeRequests',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('requesting_user', models.CharField(max_length=7)),
                ('compare_user', models.CharField(max_length=7)),
                ('action', models.CharField(max_length=10)),
                ('right_name', models.CharField(max_length=150)),
                ('right_type', models.CharField(max_length=5)),
                ('reason_for_action', models.CharField(max_length=500)),
                ('status', models.CharField(default='unanswered', max_length=10)),
                ('reason_for_decline', models.CharField(default='', max_length=500)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='userhattbluseridundname',
            name='change_requests',
            field=models.ManyToManyField(blank=True, default=None, related_name='user_change_requests', to='rapp.ChangeRequests'),
        ),
    ]