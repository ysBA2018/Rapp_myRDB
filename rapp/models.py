# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.expressions import F

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
from django.urls import reverse		# Used to generate URLs by reversing the URL patterns


# Tabelle enthält die aktuell genehmigten (modellierten und in Modellierung befindlichen) AF + GF-Kombinationen
class TblUebersichtAfGfs(models.Model):
	id = 					models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	name_gf_neu = 			models.CharField(db_column='Name GF Neu', max_length=50, blank=True, null=True, verbose_name='GF Neu')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	name_af_neu = 			models.CharField(db_column='Name AF Neu', max_length=50, blank=True, null=True, verbose_name='AF Neu')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	kommentar = 			models.CharField(db_column='Kommentar', max_length=150, blank=True, null=True)  # Field name made lowercase.
	zielperson = 			models.CharField(db_column='Zielperson', max_length=50, blank=True, null=True)  # Field name made lowercase.
	af_text = 				models.CharField(db_column='AF Text', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_text = 				models.CharField(db_column='GF Text', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_langtext = 			models.CharField(db_column='AF Langtext', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_ausschlussgruppen = 	models.CharField(db_column='AF Ausschlussgruppen', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_einschlussgruppen = 	models.CharField(db_column='AF Einschlussgruppen', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_sonstige_vergabehinweise = models.CharField(db_column='AF Sonstige Vergabehinweise', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	geloescht =				models.IntegerField(db_column='gelöscht', blank=True, null=True)
	kannweg = 				models.IntegerField(blank=True, null=True)
	modelliert = 			models.DateTimeField(blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'tblÜbersichtAF_GFs'
		unique_together = (('name_af_neu', 'name_gf_neu'), ('name_gf_neu', 'name_af_neu'),)
		verbose_name = "Erlaubte AF/GF-Kombination"
		verbose_name_plural = "Erlaubte AF/GF-Kombinationen-Übersicht (tblUebersichtAfGfs)"
		ordering = ['-id']

	def __str__(self) -> str:
		return self.name_gf_neu + ' | ' + self.name_af_neu

	geloescht.boolean = True
	kannweg.boolean = True

# Die Tabelle enthält die Teambeschreibungen. Das eigentliche Team ist das Feld intern_extern
class TblOrga(models.Model):
	id = 				models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	team = 				models.CharField(db_column='Intern - extern', unique=True, max_length=50, blank=False, null=False, default='Hä???')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	themeneigentuemer =	models.CharField(db_column='Themeneigentümer', max_length=150, blank=False, null=False, default='Hä???')  # Field name made lowercase.

	class Meta:
		managed = True
		db_table = 'tblOrga'
		verbose_name = "Orga-Information"
		verbose_name_plural = "Organisations-Übersicht (tblOrga)"
		ordering = ['team']

	def __str__(self) -> str:
		return self.team

	def get_absolute_url(self):
		# Returns the url for the item.
		return reverse('teamliste', args=[])

	def get_absolute_update_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('team-update', args=[str(self.id)])

	def get_absolute_delete_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('team-delete', args=[str(self.id)])

	def get_absolute_create_url(self):
		# Returns the url to open the create-instance of the model (no ID given, the element does not exist yet).
		return reverse('team-create', args=[])



# Die Namen aller aktiven und gelöschten UserIDen und der dazugehörenden Namen (Realnamen und Technische User)
class TblUserIDundName(models.Model):
	id = 				models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	userid = 			models.CharField(db_column='UserID', unique=True, max_length=50)  # Field name made lowercase.
	name = 				models.CharField(db_column='Name', max_length=150, blank=True, null=True)  # Field name made lowercase.
	orga = 				models.ForeignKey('TblOrga', on_delete=models.CASCADE, db_column='Orga_ID', verbose_name='Team')  # Field name made lowercase.
	zi_organisation =	models.CharField(db_column='ZI-Organisation', max_length=50, blank=True, null=True, verbose_name='ZI-Organisation')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	geloescht = 		models.IntegerField(db_column='gelöscht', blank=True, null=True, verbose_name='gelöscht')
	abteilung = 		models.CharField(db_column='Abteilung', max_length=50, blank=True, null=True)  # Field name made lowercase.
	gruppe = 			models.CharField(db_column='Gruppe', max_length=50, blank=True, null=True)  # Field name made lowercase.


	class Meta:
		managed = False
		db_table = 'tblUserIDundName'
		unique_together = (('userid', 'name'),)
		verbose_name = "UserID-Name-Kombination"
		verbose_name_plural = "UserID-Name-Übersicht (tblUserIDundName)"
		ordering = ['geloescht', 'name', '-userid']

	def __str__(self) -> str:
		return str(self.userid + ' | ' + self.name)

	def get_active(self):
		return not self.geloescht
	get_active.boolean = True
	get_active.admin_order_field = 'geloescht'
	get_active.short_description = 'aktiv'

	geloescht.boolean = True

	def colored_name(self):
		return format_html(
			'<span style="color: #{};">{}</span>',
			'21610B' if (self.get_active()) else "B40404",
			self.name,
		)
	colored_name.admin_order_field= 'name'
	colored_name.short_description = 'Name, Vorname'

	def get_absolute_url(self):
		# Returns the url for the whole list.
		return reverse('userliste', args=[])

	def get_absolute_update_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('user-update', args=[str(self.id)])

	def get_absolute_toggle_geloescht_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('user-toggle-geloescht', args=[str(self.id)])

	def get_absolute_delete_url(self):
		# Returns the url to access a particular instance of the model.
		# return reverse('user-detail', args=[str(self.id)])
		return reverse('user-delete', args=[str(self.id)])

	def get_absolute_create_url(self):
		# Returns the url to open the create-instance of the model (no ID given, the element does not exist yet).
		return reverse('user-create', args=[])


	# Todo: Suchfelder in die Listenanzeige einbauen
	# Todo: Als nächsten den Team-Dioalog bauen, dann die User hat Rolle-Kette weiter ausbauen


# Die verschiedenen technischne Plattformen (RACF, CICS, Unix, Win, AD, LDAP, test/Prod usw.)
class TblPlattform(models.Model):
	id = 						models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	tf_technische_plattform = 	models.CharField(db_column='TF Technische Plattform', unique=True, max_length=32, blank=True, null=True, verbose_name='Plattform')  # Field name made lowercase. Field renamed to remove unsuitable characters.

	class Meta:
		managed = False
		db_table = 'tblPlattform'
		verbose_name = "Plattform"
		verbose_name_plural = "Plattform-Übersicht (tblPlattform)"
		# ordering = ['tf_technische_plattform']


	def __str__(self) -> str:
		return self.tf_technische_plattform



# tblGesamt enthält alle Daten zu TFs in GFs in AFs für jeden User und seine UserIDen
class TblGesamt(models.Model):
	id = 					models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	userid_name = 			models.ForeignKey('TblUserIDundName', on_delete=models.CASCADE, db_column='UserID + Name_ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf = 					models.CharField(db_column='TF', max_length=150, verbose_name='TF')  # Field name made lowercase.
	tf_beschreibung = 		models.CharField(db_column='TF Beschreibung', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	enthalten_in_af = 		models.CharField(db_column='Enthalten in AF', max_length=150, blank=True, null=True, verbose_name='AF')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	modell = 				models.ForeignKey('TblUebersichtafGfs', on_delete=models.CASCADE, db_column='Modell')  # Field name made lowercase.
	tf_kritikalitaet = 		models.CharField(db_column='TF Kritikalität', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_eigentuemer_org = 	models.CharField(db_column='TF Eigentümer Org', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	plattform = 			models.ForeignKey('TblPlattform', on_delete=models.CASCADE, db_column='Plattform_ID', blank=True, null=True, verbose_name='Plattform')  # Field name made lowercase.
	gf = 					models.CharField(db_column='GF', max_length=150, blank=True, null=True)  # Field name made lowercase.
	vip_kennzeichen = 		models.CharField(db_column='VIP Kennzeichen', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	zufallsgenerator = 		models.CharField(db_column='Zufallsgenerator', max_length=150, blank=True, null=True)  # Field name made lowercase.
	af_gueltig_ab = 		models.DateTimeField(db_column='AF Gültig ab', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_gueltig_bis = 		models.DateTimeField(db_column='AF Gültig bis', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	direct_connect = 		models.CharField(db_column='Direct Connect', max_length=8, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	hoechste_kritikalitaet_tf_in_af = \
							models.CharField(db_column='Höchste Kritikalität TF in AF', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	gf_beschreibung = 		models.CharField(db_column='GF Beschreibung', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	af_zuweisungsdatum = 	models.DateTimeField(db_column='AF Zuweisungsdatum', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	datum = 				models.DateTimeField(db_column='Datum')  # Field name made lowercase.
	geloescht = 			models.IntegerField(db_column='gelöscht', blank=True, null=True, verbose_name='gelöscht')
	gefunden = 				models.IntegerField(blank=True, null=True)
	wiedergefunden = 		models.DateTimeField(blank=True, null=True)
	geaendert = 			models.IntegerField(db_column='geändert', blank=True, null=True)  # This field type is a guess.
	neueaf = 				models.CharField(db_column='NeueAF', max_length=50, blank=True, null=True)  # Field name made lowercase.
	nicht_ai = 				models.IntegerField(db_column='Nicht AI', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	patchdatum = 			models.DateTimeField(db_column='Patchdatum', blank=True, null=True)  # Field name made lowercase.
	wertmodellvorpatch =	models.TextField(db_column='WertModellVorPatch', blank=True, null=True)  # Field name made lowercase.
	loeschdatum = 			models.DateTimeField(db_column='löschdatum', blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'tblGesamt'
		verbose_name = "Eintrag der Gesamttabelle (tblGesamt)"
		verbose_name_plural = "Gesamttabelle Übersicht (tblGesamt)"

	def __str__(self) -> str:
		return str(self.id)

	def get_active(self):
		return not self.geloescht
	get_active.boolean = True
	get_active.admin_order_field = 'geloescht'
	get_active.short_description = 'aktiv'

	def get_gefunden(self):
		return self.gefunden
	get_gefunden.boolean = True

	def get_geaendert(self):
		return self.geaendert
	geaendert.boolean = True

	def get_direct_connect(self):
		return self.direct_connect == 'Ja'
	get_direct_connect.boolean = True
	get_direct_connect.admin_order_field = 'direct_connect'
	get_direct_connect.short_description = 'direkt'

	def get_ai(self):
		return not self.nicht_ai
	get_ai.boolean = True

	def get_absolute_url(self):
		# Returns the url to access a particular instance of the model.
		return reverse('gesamt-detail', args=[str(self.id)])


# tblGesamtHistorie enthält alle Daten zu TFs in GFs in AFs für jeden User und seine UserIDen, wenn der User (mal) gelöscht wurde
class TblGesamtHistorie(models.Model):
	id = 				models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
	wiedergefunden = 	models.DateTimeField(blank=True, null=True)
	# Das ist echt blöd, dass das hier zu lange dauert
	id_alt = 			models.ForeignKey('Tblgesamt', models.DO_NOTHING, db_column='ID-alt')  # Field name made lowercase. Field renamed to remove unsuitable characters.
	# id_alt = 			models.CharField(db_column='ID-alt', max_length=11)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	userid_name = 		models.ForeignKey('TblUserIDundName', on_delete=models.CASCADE, db_column='UserID + Name_ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf = 				models.CharField(db_column='TF', max_length=150)  # Field name made lowercase.
	tf_beschreibung = 	models.CharField(db_column='TF Beschreibung', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	enthalten_in_af = 	models.CharField(db_column='Enthalten in AF', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	modell = 			models.ForeignKey('TblUebersichtafGfs', on_delete=models.CASCADE, db_column='Modell')  # Field name made lowercase.
	tf_kritikalitaet = 	models.CharField(db_column='TF Kritikalität', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	tf_eigentuemer_org =	models.CharField(db_column='TF Eigentümer Org', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	plattform = 		models.ForeignKey('TblPlattform', on_delete=models.CASCADE, db_column='Plattform_ID', blank=True, null=True)  # Field name made lowercase.
	gf = 				models.CharField(db_column='GF', max_length=150, blank=True, null=True)  # Field name made lowercase.
	vip_kennzeichen = 	models.CharField(db_column='VIP Kennzeichen', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
	zufallsgenerator =	models.CharField(db_column='Zufallsgenerator', max_length=150, blank=True, null=True)  # Field name made lowercase.
	datum = 			models.DateTimeField(db_column='Datum')  # Field name made lowercase.
	geloescht =			models.TextField(db_column='gelöscht', blank=True, null=True)  # This field type is a guess.
	gefunden = 			models.TextField(blank=True, null=True)  # This field type is a guess.
	geaendert =			models.TextField(db_column='geändert', blank=True, null=True)  # This field type is a guess.
	neueaf = 			models.CharField(db_column='NeueAF', max_length=50, blank=True, null=True)  # Field name made lowercase.
	loeschdatum = 		models.DateTimeField(db_column='Löschdatum', blank=True, null=True)  # Field name made lowercase.

	class Meta:
		managed = True
		db_table = 'tblGesamtHistorie'
		verbose_name = "Historisierter Eintrag der Gesamttabelle (tblGesamtHistorie)"
		verbose_name_plural = "Historisierte Einträge der Gesamttabelle (tblGesamtHistorie)"

	def __str__(self) -> str:
		return str(self.id)

