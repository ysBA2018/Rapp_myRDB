# Generated by Django 2.2.1 on 2019-08-09 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0005_auto_20190731_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblplattform',
            name='color',
            field=models.CharField(default='0', max_length=25, null=True),
        ),
    ]
