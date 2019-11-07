# Generated by Django 2.2.1 on 2019-09-24 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0016_auto_20190912_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='TblTf',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('tf', models.CharField(db_column='tf', db_index=True, max_length=100, verbose_name='TF')),
                ('tf_beschreibung', models.CharField(blank=True, db_column='tf_beschreibung', max_length=250, null=True, verbose_name='TF-Beschreibung')),
                ('tf_kritikalitaet', models.CharField(blank=True, db_column='tf_kritikalitaet', db_index=True, max_length=64, null=True, verbose_name='TF-Kritikalität')),
                ('tf_eigentuemer_org', models.CharField(blank=True, db_column='tf_eigentuemer_org', db_index=True, max_length=64, null=True, verbose_name='TF-Eigentümer-orga')),
                ('vip_kennzeichen', models.CharField(blank=True, db_column='vip', max_length=32, null=True, verbose_name='VIP')),
                ('zufallsgenerator', models.CharField(blank=True, db_column='zufallsgenerator', max_length=32, null=True, verbose_name='Zufallsgenerator')),
                ('direct_connect', models.CharField(blank=True, db_column='direct_connect', max_length=100, null=True, verbose_name='Direktverbindung')),
                ('datum', models.DateTimeField(db_column='datum', db_index=True, verbose_name='Recht gefunden am')),
                ('geloescht', models.IntegerField(blank=True, db_column='geloescht', db_index=True, null=True, verbose_name='gelöscht')),
                ('gefunden', models.IntegerField(blank=True, db_index=True, null=True)),
                ('wiedergefunden', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('geaendert', models.IntegerField(blank=True, db_column='geaendert', db_index=True, null=True, verbose_name='AF geändert')),
                ('nicht_ai', models.IntegerField(blank=True, db_column='nicht_ai', null=True)),
                ('patchdatum', models.DateTimeField(blank=True, db_column='patchdatum', db_index=True, null=True)),
                ('wertmodellvorpatch', models.TextField(blank=True, db_column='wert_modell_vor_patch', null=True)),
                ('loeschdatum', models.DateTimeField(blank=True, db_column='loeschdatum', db_index=True, null=True, verbose_name='Löschdatum')),
                ('letzte_aenderung', models.DateTimeField(auto_now=True, db_index=True)),
                ('plattform', models.ForeignKey(db_column='plattform_id', on_delete=django.db.models.deletion.CASCADE, to='rapp.TblPlattform', verbose_name='Plattform')),
            ],
        ),
    ]