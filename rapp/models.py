# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your models here.

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from django.utils.html import format_html

# Tabelle enthält die aktuell genehmigten (modellierten und in Modellierung befindlichen) AF + GF-Kombinationen
class TblUebersichtAfGfs(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	name_gf_neu = models.CharField(db_column='Name GF Neu', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	name_af_neu = models.CharField(db_column='Name AF Neu', max_length=50)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	kommentar = models.CharField(db_column='Kommentar', max_length=150, blank=True, null=True)  # Field name made lowercase.
	zielperson = models.CharField(db_column='Zielperson', max_length=50, blank=True, null=True)  # Field name made lowercase.
	af_text = models.CharField(db_column='AF Text', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_text = models.CharField(db_column='GF Text', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_langtext = models.CharField(db_column='AF Langtext', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_ausschlussgruppen = models.CharField(db_column='AF Ausschlussgruppen', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_einschlussgruppen = models.CharField(db_column='AF Einschlussgruppen', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_sonstige_vergabehinweise = models.CharField(db_column='AF Sonstige Vergabehinweise', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	geloescht = models.IntegerField(db_column='gelöscht', blank=True, null=True)
	kannweg = models.IntegerField(blank=True, null=True)
	modelliert = models.DateTimeField(blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'tblÜbersichtAF_GFs'
		unique_together = (('name_af_neu', 'name_gf_neu'), ('name_gf_neu', 'name_af_neu'),)

	def __str__(self) -> str:
		return self.name_gf_neu + ' | ' + self.name_af_neu

	geloescht.boolean = True
	kannweg.boolean = True

# Die Tabelle enthält die Teambeschreibungen. Das eigentliche Team ist das Feld intern_extern
class TblOrga(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	team = models.CharField(db_column='Intern - extern', unique=True, max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	themeneigentuemer = models.CharField(db_column='Themeneigentümer', max_length=150, blank=True, null=True)  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = 'tblOrga'

	def __str__(self) -> str:
		return self.team

# Die ANmen aller aktiven und gelöschten UserIDen und der dazugehörenden Namen (Realnamen und Technische User)
class TblUserIDundName(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	userid = models.CharField(db_column='UserID', unique=True, max_length=50)  # Field name made lowercase.
	name = models.CharField(db_column='Name', max_length=150, blank=True, null=True)  # Field name made lowercase.
	orga = models.ForeignKey('TblOrga', on_delete=models.CASCADE, db_column='Orga_ID')  # Field name made lowercase.
	zi_organisation = models.CharField(db_column='ZI-Organisation', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	geloescht = models.IntegerField(db_column='gelöscht', blank=True, null=True)
	abteilung = models.CharField(db_column='Abteilung', max_length=50, blank=True, null=True)  # Field name made lowercase.
	gruppe = models.CharField(db_column='Gruppe', max_length=50, blank=True, null=True)  # Field name made lowercase.


	class Meta:
		managed = False
		db_table = 'tblUserIDundName'
		unique_together = (('userid', 'name'),)

	def __str__(self) -> str:
		return self.userid + ' | ' + self.name

	def get_active(self):
		return not self.geloescht
	get_active.boolean = True
	get_active.admin_order_field = 'geloescht'
	get_active.short_description = 'aktiv'

	def colored_name(self):
		return format_html(
			'<span style="color: #{};">{}</span>',
			'21610B' if (self.get_active()) else "B40404",
			self.name,
		)
	colored_name.admin_order_field= 'name'
	colored_name.short_description = 'Name, Vorname'



# Die verschiedenen technischne Plattformen (RACF, CICS, Unix, Win, AD, LDAP, test/Prod usw.)
class TblPlattform(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	tf_technische_plattform = models.CharField(db_column='TF Technische Plattform', unique=True, max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

	class Meta:
		managed = False
		db_table = 'tblPlattform'

	def __str__(self) -> str:
		return self.tf_technische_plattform

# tblGesamt enthält alle Daten zu TFs in GFs in AFs für jeden User und seine UserIDen
class TblGesamt(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	userid_name = models.ForeignKey('TblUserIDundName', on_delete=models.CASCADE, db_column='UserID + Name_ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf = models.CharField(db_column='TF', max_length=150)  # Field name made lowercase.
	tf_beschreibung = models.CharField(db_column='TF Beschreibung', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	enthalten_in_af = models.CharField(db_column='Enthalten in AF', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	modell = models.ForeignKey('TblUebersichtafGfs', on_delete=models.CASCADE, db_column='Modell')  # Field name made lowercase.
	tf_kritikalitaet = models.CharField(db_column='TF Kritikalität', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_eigentuemer_org = models.CharField(db_column='TF Eigentümer Org', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	plattform = models.ForeignKey('TblPlattform', on_delete=models.CASCADE, db_column='Plattform_ID', blank=True, null=True)  # Field name made lowercase.
	gf = models.CharField(db_column='GF', max_length=150, blank=True, null=True)  # Field name made lowercase.
	vip_kennzeichen = models.CharField(db_column='VIP Kennzeichen', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	zufallsgenerator = models.CharField(db_column='Zufallsgenerator', max_length=150, blank=True, null=True)  # Field name made lowercase.
	af_gueltig_ab = models.DateTimeField(db_column='AF Gültig ab', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_gueltig_bis = models.DateTimeField(db_column='AF Gültig bis', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	direct_connect = models.CharField(db_column='Direct Connect', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	hoechste_kritikalitaet_tf_in_af = models.CharField(db_column='Höchste Kritikalität TF in AF', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_beschreibung = models.CharField(db_column='GF Beschreibung', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_zuweisungsdatum = models.DateTimeField(db_column='AF Zuweisungsdatum', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	datum = models.DateTimeField(db_column='Datum')  # Field name made lowercase.
	geloescht = models.IntegerField(db_column='gelöscht', blank=True, null=True)
	gefunden = models.IntegerField(blank=True, null=True)
	wiedergefunden = models.DateTimeField(blank=True, null=True)
	geaendert = models.IntegerField(db_column='geändert', blank=True, null=True)  # This field type is a guess.
	neueaf = models.CharField(db_column='NeueAF', max_length=50, blank=True, null=True)  # Field name made lowercase.
	nicht_ai = models.IntegerField(db_column='Nicht AI', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	patchdatum = models.DateTimeField(db_column='Patchdatum', blank=True, null=True)  # Field name made lowercase.
	wertmodellvorpatch = models.TextField(db_column='WertModellVorPatch', blank=True, null=True)  # Field name made lowercase.
	loeschdatum = models.DateTimeField(db_column='löschdatum', blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'tblGesamt'

	geloescht.boolean = True
	gefunden.boolean = True

