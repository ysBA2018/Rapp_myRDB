# Generated by Django 2.2.1 on 2019-09-09 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0008_tbluebersichtafgfs_tfs'),
    ]

    operations = [
        migrations.AddField(
            model_name='tblappliedaf',
            name='delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tblappliedaf',
            name='transfer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tblappliedgf',
            name='delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tblappliedgf',
            name='transfer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tblappliedrolle',
            name='delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tblappliedrolle',
            name='transfer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tblappliedtf',
            name='delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tblappliedtf',
            name='transfer',
            field=models.BooleanField(default=False),
        ),
    ]
