# Generated by Django 2.2.1 on 2019-09-09 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0009_auto_20190909_1136'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tblappliedaf',
            old_name='delete',
            new_name='deleted',
        ),
        migrations.RenameField(
            model_name='tblappliedaf',
            old_name='transfer',
            new_name='transfered',
        ),
        migrations.RenameField(
            model_name='tblappliedgf',
            old_name='delete',
            new_name='deleted',
        ),
        migrations.RenameField(
            model_name='tblappliedgf',
            old_name='transfer',
            new_name='transfered',
        ),
        migrations.RenameField(
            model_name='tblappliedrolle',
            old_name='delete',
            new_name='deleted',
        ),
        migrations.RenameField(
            model_name='tblappliedrolle',
            old_name='transfer',
            new_name='transfered',
        ),
        migrations.RenameField(
            model_name='tblappliedtf',
            old_name='delete',
            new_name='deleted',
        ),
        migrations.RenameField(
            model_name='tblappliedtf',
            old_name='transfer',
            new_name='transfered',
        ),
    ]
