# Generated by Django 2.1 on 2018-10-04 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0015_auto_20181004_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tblrechteneuvonimport',
            name='tf_name',
            field=models.CharField(blank=True, db_column='TF Name', max_length=100, null=True),
        ),
    ]
