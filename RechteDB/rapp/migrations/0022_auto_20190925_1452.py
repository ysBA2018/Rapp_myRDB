# Generated by Django 2.2.1 on 2019-09-25 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0021_auto_20190925_1441'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tbltf',
            name='tf_schreibweise',
        ),
        migrations.CreateModel(
            name='TblTfHatSchreibweise',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('schreibweise_id', models.ForeignKey(db_column='schreibweise_id', default=None, on_delete=django.db.models.deletion.CASCADE, to='rapp.TblSchreibweisen')),
                ('tf_id', models.ForeignKey(db_column='tf_id', on_delete=django.db.models.deletion.CASCADE, to='rapp.TblTf')),
            ],
        ),
    ]
