# Generated by Django 2.2.1 on 2019-09-10 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0011_auto_20190910_1007'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userhattbluseridundname',
            old_name='change_requests',
            new_name='my_requests',
        ),
    ]
