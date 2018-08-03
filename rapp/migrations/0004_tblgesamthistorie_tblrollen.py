# Generated by Django 2.0.7 on 2018-08-01 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rapp', '0003_auto_20180801_2243'),
    ]

    operations = [
        migrations.CreateModel(
            name='TblGesamtHistorie',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('wiedergefunden', models.DateTimeField(blank=True, null=True)),
                ('tf', models.CharField(db_column='TF', max_length=150)),
                ('tf_beschreibung', models.CharField(blank=True, db_column='TF Beschreibung', max_length=150, null=True)),
                ('enthalten_in_af', models.CharField(blank=True, db_column='Enthalten in AF', max_length=150, null=True)),
                ('tf_kritikalitaet', models.CharField(blank=True, db_column='TF Kritikalität', max_length=150, null=True)),
                ('tf_eigentuemer_org', models.CharField(blank=True, db_column='TF Eigentümer Org', max_length=150, null=True)),
                ('gf', models.CharField(blank=True, db_column='GF', max_length=150, null=True)),
                ('vip_kennzeichen', models.CharField(blank=True, db_column='VIP Kennzeichen', max_length=150, null=True)),
                ('zufallsgenerator', models.CharField(blank=True, db_column='Zufallsgenerator', max_length=150, null=True)),
                ('datum', models.DateTimeField(db_column='Datum')),
                ('geloescht', models.TextField(blank=True, db_column='gelöscht', null=True)),
                ('gefunden', models.TextField(blank=True, null=True)),
                ('geaendert', models.TextField(blank=True, db_column='geändert', null=True)),
                ('neueaf', models.CharField(blank=True, db_column='NeueAF', max_length=50, null=True)),
                ('loeschdatum', models.DateTimeField(blank=True, db_column='Löschdatum', null=True)),
                ('id_alt', models.ForeignKey(db_column='ID-alt', on_delete=django.db.models.deletion.DO_NOTHING, to='rapp.TblGesamt')),
                ('modell', models.ForeignKey(db_column='Modell', on_delete=django.db.models.deletion.CASCADE, to='rapp.TblUebersichtAfGfs')),
                ('plattform', models.ForeignKey(blank=True, db_column='Plattform_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='rapp.TblPlattform')),
                ('userid_name', models.ForeignKey(blank=True, db_column='UserID + Name_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='rapp.TblUserIDundName')),
            ],
            options={
                'verbose_name_plural': 'Historisierte Einträge der Gesamttabelle (tblGesamtHistorie)',
                'managed': True,
                'db_table': 'tblGesamtHistorie',
                'verbose_name': 'Historisierter Eintrag der Gesamttabelle (tblGesamtHistorie)',
            },
        ),
        migrations.CreateModel(
            name='TblRollen',
            fields=[
                ('rollenname', models.CharField(db_column='RollenName', max_length=150, primary_key=True, serialize=False, verbose_name='Rollen-Name')),
                ('system', models.CharField(db_column='System', max_length=150, verbose_name='System')),
                ('rollenbeschreibung', models.TextField(blank=True, db_column='RollenBeschreibung', null=True)),
                ('datum', models.DateTimeField(db_column='Datum')),
            ],
            options={
                'managed': True,
                'db_table': 'tbl_Rollen',
                'verbose_name_plural': 'Rollen-Übersicht (tbl_Rollen)',
                'ordering': ['rollenname'],
                'verbose_name': 'Rollenliste',
            },
        ),
    ]
