# -*- coding: utf-8 -*-
# Create your models here.

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth import get_user_model

from django.db import models
from django.utils.html import format_html
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
from django.utils import timezone
from django.db import connection
from django.dispatch import receiver

from django.db.models.signals import post_save
from RechteDB import settings
from rest_framework.authtoken.models import Token


# tblGesamt enthält alle Daten zu TFs in GFs in AFs für jeden User und seine UserIDen
class TblGesamt(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    userid_name = models.ForeignKey('TblUserIDundName', db_column='userid_und_name_id', on_delete=models.CASCADE,
                                    db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf = models.CharField(db_column='tf', max_length=100, verbose_name='TF',
                          db_index=True)  # Field name made lowercase.
    tf_beschreibung = models.CharField(db_column='tf_beschreibung', max_length=250, blank=True, null=True,
                                       verbose_name='TF-Beschreibung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    enthalten_in_af = models.CharField(db_column='enthalten_in_af', max_length=100, blank=True, null=True,
                                       verbose_name='AF',
                                       db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    modell = models.ForeignKey('TblUebersichtAfGfs', db_column='modell', on_delete=models.CASCADE,
                               db_index=True)  # Field name made lowercase.
    tf_kritikalitaet = models.CharField(db_column='tf_kritikalitaet', max_length=64, blank=True, null=True,
                                        verbose_name='TF-Kritikalität',
                                        db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_eigentuemer_org = models.CharField(db_column='tf_eigentuemer_org', max_length=64, blank=True, null=True,
                                          verbose_name='TF-Eigentümer-orga',
                                          db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    plattform = models.ForeignKey('TblPlattform', db_column='plattform_id', on_delete=models.CASCADE,
                                  verbose_name='Plattform', db_index=True)  # Field name made lowercase.
    gf = models.CharField(db_column='gf', max_length=100, blank=True, null=True, verbose_name='GF',
                          db_index=True)  # Field name made lowercase.
    vip_kennzeichen = models.CharField(db_column='vip', max_length=32, blank=True, null=True,
                                       verbose_name='VIP')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    zufallsgenerator = models.CharField(db_column='zufallsgenerator', max_length=32, blank=True, null=True,
                                        verbose_name='Zufallsgenerator')  # Field name made lowercase.
    af_gueltig_ab = models.DateTimeField(db_column='af_gueltig_ab', blank=True, null=True,
                                         verbose_name='AF gültig ab')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_gueltig_bis = models.DateTimeField(db_column='af_gueltig_bis', blank=True, null=True,
                                          verbose_name='AF gültig bis')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    direct_connect = models.CharField(db_column='direct_connect', max_length=100, blank=True, null=True,
                                      verbose_name='Direktverbindung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    hoechste_kritikalitaet_tf_in_af = \
        models.CharField(db_column='hk_tf_in_af', max_length=150, blank=True, null=True,
                         verbose_name='max. Krit. TF in AF')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gf_beschreibung = models.CharField(db_column='gf_beschreibung', max_length=250, blank=True, null=True,
                                       verbose_name='GF Kurzbeschreibung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_zuweisungsdatum = models.DateTimeField(db_column='af_zuweisungsdatum', blank=True, null=True,
                                              verbose_name='AF Zuweisung',
                                              db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    datum = models.DateTimeField(db_column='datum', verbose_name='Recht gefunden am',
                                 db_index=True)  # Field name made lowercase.
    geloescht = models.IntegerField(db_column='geloescht', blank=True, null=True, verbose_name='gelöscht',
                                    db_index=True)
    gefunden = models.IntegerField(blank=True, null=True, db_index=True)
    wiedergefunden = models.DateTimeField(blank=True, null=True, db_index=True)
    geaendert = models.IntegerField(db_column='geaendert', blank=True, null=True, verbose_name='AF geändert',
                                    db_index=True)  # This field type is a guess.
    neueaf = models.CharField(db_column='neueaf', max_length=50, blank=True, null=True,
                              db_index=True)  # Field name made lowercase.
    nicht_ai = models.IntegerField(db_column='nicht_ai', blank=True,
                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    patchdatum = models.DateTimeField(db_column='patchdatum', blank=True, null=True,
                                      db_index=True)  # Field name made lowercase.
    wertmodellvorpatch = models.TextField(db_column='wert_modell_vor_patch', blank=True,
                                          null=True)  # Field name made lowercase.
    loeschdatum = models.DateTimeField(db_column='loeschdatum', blank=True, null=True, verbose_name='Löschdatum',
                                       db_index=True)
    letzte_aenderung = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        managed = True
        db_table = 'tblGesamt'
        verbose_name = "Eintrag der Gesamttabelle (tblGesamt)"
        verbose_name_plural = "08_Gesamttabelle Übersicht (tblGesamt)"
        index_together = (
            ('userid_name', 'tf', 'enthalten_in_af', 'plattform', 'gf', 'vip_kennzeichen', 'zufallsgenerator'),)
        ordering = ['id']

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


# Tabelle enthält die aktuell genehmigten (modellierten und in Modellierung befindlichen) AF + GF-Kombinationen
class TblUebersichtAfGfs(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    name_gf_neu = models.CharField(db_column='name_gf_neu', max_length=100, verbose_name='GF Neu',
                                   db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    name_af_neu = models.CharField(db_column='name_af_neu', max_length=50, verbose_name='AF Neu',
                                   db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    kommentar = models.CharField(db_column='kommentar', max_length=150, blank=True,
                                 null=True)  # Field name made lowercase.
    zielperson = models.CharField(db_column='zielperson', max_length=50, )  # Field name made lowercase.
    af_text = models.CharField(db_column='af_text', max_length=150, blank=True,
                               null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gf_text = models.CharField(db_column='gf_text', max_length=150, blank=True,
                               null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_langtext = models.CharField(db_column='af_langtext', max_length=250, blank=True,
                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_ausschlussgruppen = models.CharField(db_column='af_ausschlussgruppen', max_length=250, blank=True,
                                            null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_einschlussgruppen = models.CharField(db_column='af_einschlussgruppen', max_length=250, blank=True,
                                            null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_sonstige_vergabehinweise = models.CharField(db_column='af_sonstige_vergabehinweise', max_length=250, blank=True,
                                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    geloescht = models.IntegerField(db_column='geloescht', blank=True, null=True, db_index=True)
    kannweg = models.IntegerField(blank=True, null=True)
    modelliert = models.DateTimeField(blank=True, null=True)
    tfs = models.ManyToManyField(to=TblGesamt,through='TblGfHatTF',related_name='model_gf_hat_tfs',default=None)

    class Meta:
        managed = True
        db_table = 'tblUEbersichtAF_GFs'
        unique_together = (('name_af_neu', 'name_gf_neu'), ('name_gf_neu', 'name_af_neu'),)
        verbose_name = "Erlaubte AF/GF-Kombination"
        verbose_name_plural = "04_Erlaubte AF/GF-Kombinationen-Übersicht (tblUebersichtAF_GFs)"
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name_gf_neu + ' | ' + self.name_af_neu

    geloescht.boolean = True
    kannweg.boolean = True


class TblGfHatTF(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    gf_id = models.ForeignKey('TblUebersichtAfGfs', db_column='gf_id', on_delete=models.CASCADE)
    tf_id = models.ForeignKey('TblGesamt', db_column='tf_id', on_delete=models.CASCADE,default=None)



# Dies ist nur eine Hilfstabelle.
# Sie besteht aus dem `tblÜbersichtAF_GFs`.`Name AF Neu` für alle Felder, bei denen `modelliert` nicht null ist.
# (das automatisch ergänzte Datum wird nicht benötigt, hier könnte auch das `modelliert`genommen werden)
# Original Query im Access:_
#
# INSERT INTO tbl_AFListe ( [AF-Name] )
#  SELECT tblÜbersichtAF_GFs.[Name AF Neu]
#  FROM tblÜbersichtAF_GFs LEFT JOIN tbl_AFListe ON tblÜbersichtAF_GFs.[Name AF Neu] = tbl_AFListe.[AF-Name]
#  WHERE (((tblÜbersichtAF_GFs.modelliert) Is Not Null) AND ((tbl_AFListe.[AF-Name]) Is Null))
#  GROUP BY tblÜbersichtAF_GFs.[Name AF Neu];
#
# Sinn der Tabelle ist, eine eindeutige Liste an AFs vorliegen zu haben. Das GROUP- BY kann evtl teuer werden.
# Aber das probieren wir jetzt mal aus.
class TblAfliste(models.Model):
    id = models.AutoField(db_column='id', primary_key=True, verbose_name='ID')  # Field name made lowercase.
    af_name = models.CharField(db_column='af_name', unique=True, max_length=150,
                               verbose_name='AF-Name')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    neu_ab = models.DateTimeField(db_column='neu_ab')  # Field renamed to remove unsuitable characters.
    gfs = models.ManyToManyField(to=TblUebersichtAfGfs, through='TblAfHatGF', related_name='model_af_hat_gfs',default=None)
    class Meta:
        managed = True
        db_table = 'tbl_AFListe'
        verbose_name = "Gültige AF"
        verbose_name_plural = "98_Übersicht gültiger AFen (tbl_AFListe)"
        ordering = ['af_name']

    def __str__(self) -> str:
        return str(self.af_name)

class TblAfHatGF(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    gf_id = models.ForeignKey('TblUebersichtAfGfs', db_column='gf_id', on_delete=models.CASCADE)
    af_id = models.ForeignKey('TblAfliste', db_column='af_id', on_delete=models.CASCADE,default=None)


# class TblGfliste(models.Model):


# Die drei Rollentabellen sowie die AF-Liste hängen inhaltlich zusammen
# Die Definition der Rollen
class TblAppliedTf(models.Model):
    id = models.AutoField(primary_key=True)
    model_tf_id = models.ForeignKey(to='TblGesamt', on_delete=models.PROTECT)
    userHatUserID_id = models.ForeignKey(to='UserHatTblUserIDundName', on_delete=models.PROTECT)
    applied_rolle_id = models.ForeignKey(to='TblAppliedRolle', on_delete=models.PROTECT)
    applied_af_id = models.ForeignKey(to='TblAppliedAf', on_delete=models.PROTECT)
    applied_gf_id = models.ForeignKey(to='TblAppliedGf', on_delete=models.PROTECT)


class TblAppliedGf(models.Model):
    id = models.AutoField(primary_key=True)
    model_gf_id = models.ForeignKey(to='TblUebersichtAfGfs', on_delete=models.PROTECT)
    userHatUserID_id = models.ForeignKey(to='UserHatTblUserIDundName', on_delete=models.PROTECT)
    applied_rolle_id = models.ForeignKey(to='TblAppliedRolle', on_delete=models.PROTECT)
    applied_af_id = models.ForeignKey(to='TblAppliedAf', on_delete=models.PROTECT)
    applied_tfs = models.ManyToManyField(to='TblAppliedTf', related_name='applied_tfs', default=None)


class TblAppliedAf(models.Model):
    id = models.AutoField(primary_key=True)
    model_af_id = models.ForeignKey(to='TblAfliste',on_delete=models.PROTECT)
    userHatUserID_id = models.ForeignKey(to='UserHatTblUserIDundName',on_delete=models.PROTECT)
    applied_rolle_id = models.ForeignKey(to='TblAppliedRolle', on_delete=models.PROTECT)
    applied_gfs = models.ManyToManyField(to='TblAppliedGf',related_name='applied_gfs',default=None)


class TblAppliedRolle(models.Model):
    id = models.AutoField(primary_key=True)
    model_rolle_id = models.ForeignKey(to='TblRollen', to_field='rollenid',on_delete=models.PROTECT)
    userHatUserID_id = models.ForeignKey(to='UserHatTblUserIDundName',on_delete=models.PROTECT)
    applied_afs = models.ManyToManyField(to='TblAppliedAf',related_name='applied_afs',default=None)


class TblRollen(models.Model):
    rollenid = models.AutoField(primary_key=True)
    rollenname = models.CharField(db_column='rollenname', unique=True, max_length=100, verbose_name='Rollen-Name')
    system = models.CharField(db_column='system', max_length=150, verbose_name='System', db_index=True)
    rollenbeschreibung = models.TextField(db_column='rollenbeschreibung', blank=True, null=True)
    datum = models.DateTimeField(db_column='datum', default=timezone.now, blank=True)
    afs = models.ManyToManyField(to=TblAfliste, through='TblRollehataf', related_name='model_role_has_afs', default=None)

    class Meta:
        managed = True
        db_table = 'tbl_Rollen'
        verbose_name = "Rollenliste"
        verbose_name_plural = "03_Rollen-Übersicht (tbl_Rollen)"
        ordering = ['rollenname']
        unique_together = (('rollenname', 'system'),)

    def __str__(self) -> str:
        return str(self.rollenname)


# Meta-Tabelle, welche Arbeitsplatzfunktion in welcher Rolle enthalten ist (n:m Beziehung)
#
# Die drei ursprünglichen Einzelfelder nurXV, XABCV und DV wurden zusammengefast zu einer Col: einsatz:
# 	einsatz = 8:	Nur gültig für AV, BV, CV-User (z.B. Zweituser-Recht)
#	einsatz = 4:	Nur gültig für XV-Userid
#	einsatz = 2: 	Gültig für alles außer DV-User
#	einsatz = 1:	Nur gültig für DV-User
class TblRollehataf(models.Model):
    EINSATZ_NONE = 0
    EINSATZ_NURDV = 1
    EINSATZ_XABCV = 2
    EINSATZ_NURXV = 4
    EINSATZ_ABCV = 8
    EINSATZ_CHOICES = (
        (EINSATZ_NONE, 'nicht zugewiesen'),
        (EINSATZ_NURDV, 'Nur DV-User'),
        (EINSATZ_XABCV, 'XV, AV, BV, CV'),
        (EINSATZ_NURXV, 'nur XV-User'),
        (EINSATZ_ABCV, 'AV, BV, CV'),
    )

    rollenmappingid = models.AutoField(db_column='rollenmappingid', primary_key=True,
                                       verbose_name='ID')  # Field name made lowercase.
    rollenname = models.ForeignKey('TblRollen', models.PROTECT, to_field='rollenname',
                                   db_column='rollenname')  # Field name made lowercase.
    af = models.ForeignKey('TblAfliste', models.PROTECT, to_field='id', db_column='af', blank=True, null=True,
                           verbose_name='AF')  # Field name made lowercase.
    mussfeld = models.IntegerField(db_column='mussfeld', blank=True, null=True,
                                   verbose_name='Muss')  # Field name made lowercase. This field type is a guess.
    bemerkung = models.CharField(db_column='bemerkung', max_length=250, blank=True,
                                 null=True)  # Field name made lowercase.
    einsatz = models.IntegerField(db_column='einsatz', choices=EINSATZ_CHOICES, default=EINSATZ_NONE)

    class Meta:
        managed = True
        db_table = 'tbl_RolleHatAF'
        unique_together = (('rollenname', 'af'),)
        verbose_name = "Rolle und ihre Arbeitsplatzfunktionen"
        verbose_name_plural = "02_Rollen und ihre Arbeitsplatzfunktionen (tbl_RolleHatAF)"
        ordering = ['rollenname__rollenname', 'af__af_name', ]

    def __str__(self) -> str:
        return str(self.rollenname)

    def get_muss(self):
        return self.mussfeld

    get_muss.boolean = True
    get_muss.admin_order_field = 'mussfeld'
    get_muss.short_description = 'Muss'
    mussfeld.boolean = True

# Referenz der User auf die ihnen zur Verfügung stehenden Rollen
class TblUserhatrolle(models.Model):
    SCHWERPUNKT_TYPE = (
        ('Schwerpunkt', 'Schwerpunktaufgabe'),
        ('Vertretung', 'Vertretungstätigkeiten, Zweitsysteme'),
        ('Allgemein', 'Rollen, die nicht Systemen zugeordnet sind'),
    )
    userundrollenid = models.AutoField(db_column='userundrollenid', primary_key=True,
                                       verbose_name='ID')  # Field name made lowercase.
    userid = models.ForeignKey('TblUserIDundName', models.PROTECT, to_field='userid', db_column='userid',
                               verbose_name='UserID, Name', null=True)  # Field name made lowercase.
    rollenname = models.ForeignKey('TblRollen', models.PROTECT, to_field='rollenname',
                                   db_column='rollenname')  # Field name made lowercase.
    schwerpunkt_vertretung = models.CharField(db_column='schwerpunkt_vertretung',
                         max_length=100,
                         blank=True, null=True,
                         choices=SCHWERPUNKT_TYPE,
                         db_index=True
                         )  # Field name made lowercase. Field renamed to remove unsuitable characters.
    bemerkung = models.TextField(db_column='bemerkung', blank=True, null=True)  # Field name made lowercase.
    letzte_aenderung = models.DateTimeField(db_column='letzte_aenderung', default=timezone.now, blank=True,
                                            db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'tbl_UserHatRolle'
        verbose_name = "User und Ihre Rollen"
        verbose_name_plural = "01_User und Ihre Rollen (tbl_UserHatRolle)"
        ordering = ['userid__name', '-userid__userid', 'schwerpunkt_vertretung', 'rollenname', ]
        unique_together = (('userid', 'rollenname'),)

    def __str__(self) -> str:
        return str(self.userundrollenid)

    def get_rollenbeschreibung(self):
        return str(self.rollenname.rollenbeschreibung)

    get_rollenbeschreibung.short_description = 'Rollenbeschreibung'

    def get_absolute_url(self):
        # Returns the url for the whole list.
        return reverse('user_rolle_af', args=[])

    def get_absolute_update_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('user_rolle_af-update', args=[str(self.userundrollenid)])

    def get_absolute_create_url(self):
        # Returns the url to open the create-instance of the model (no ID given, the element does not exist yet).
        return reverse('user_rolle_af-create', args=[])

    def get_absolute_delete_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('user_rolle_af-delete', args=[str(self.userundrollenid)])

'''
class TblUserhatrolle_Geloescht(models.Model):
    SCHWERPUNKT_TYPE = (
        ('Schwerpunkt', 'Schwerpunktaufgabe'),
        ('Vertretung', 'Vertretungstätigkeiten, Zweitsysteme'),
        ('Allgemein', 'Rollen, die nicht Systemen zugeordnet sind'),
    )

    userundrollenid = models.AutoField(db_column='userundrollenid', primary_key=True,
                                       verbose_name='ID')  # Field name made lowercase.
    userid = models.ForeignKey('TblUserIDundName', models.PROTECT, to_field='userid', db_column='userid',
                               verbose_name='UserID, Name')  # Field name made lowercase.
    rollenname = models.ForeignKey('TblRollen', models.PROTECT, to_field='rollenname',
                                   db_column='rollenname')  # Field name made lowercase.
    schwerpunkt_vertretung = \
        models.CharField(db_column='schwerpunkt_vertretung',
                         max_length=100,
                         blank=True, null=True,
                         choices=SCHWERPUNKT_TYPE,
                         db_index=True
                         )  # Field name made lowercase. Field renamed to remove unsuitable characters.
    bemerkung = models.TextField(db_column='bemerkung', blank=True, null=True)  # Field name made lowercase.
    letzte_aenderung = models.DateTimeField(db_column='letzte_aenderung', default=timezone.now, blank=True,
                                            db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    userHatUserID_id = models.ForeignKey('UserHatTblUserIDundName_Geloescht', models.CASCADE,
                                         db_column='userHatUserID_id', default=None)  # Field name made lowercase.

    del_afs = models.ManyToManyField(TblAfliste, through='TblRollehataf_Geloescht', default=None,
                                     related_name='del_afs')
    on_delete_list = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'tbl_UserHatRolle_Geloescht'
        verbose_name = "User und Ihre Rollen Geloescht"
        verbose_name_plural = "01_User und Ihre Rollen (tbl_UserHatRolle) Geloescht"
        ordering = ['userid__name', '-userid__userid', 'schwerpunkt_vertretung', 'rollenname', ]
        unique_together = (('userid', 'rollenname'),)

    def __str__(self) -> str:
        return str(self.userundrollenid)

    def get_rollenbeschreibung(self):
        return str(self.rollenname.rollenbeschreibung)

    get_rollenbeschreibung.short_description = 'Rollenbeschreibung'

    def get_absolute_url(self):
        # Returns the url for the whole list.
        return reverse('user_rolle_af', args=[])

    def get_absolute_update_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('user_rolle_af-update', args=[str(self.userundrollenid)])

    def get_absolute_create_url(self):
        # Returns the url to open the create-instance of the model (no ID given, the element does not exist yet).
        return reverse('user_rolle_af-create', args=[])

    def get_absolute_delete_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('user_rolle_af-delete', args=[str(self.userundrollenid)])


class TblUserhatrolle_Transferiert(models.Model):
    SCHWERPUNKT_TYPE = (
        ('Schwerpunkt', 'Schwerpunktaufgabe'),
        ('Vertretung', 'Vertretungstätigkeiten, Zweitsysteme'),
        ('Allgemein', 'Rollen, die nicht Systemen zugeordnet sind'),
    )

    userundrollenid = models.AutoField(db_column='userundrollenid', primary_key=True,
                                       verbose_name='ID')  # Field name made lowercase.
    userid = models.ForeignKey('TblUserIDundName', models.PROTECT, to_field='userid', db_column='userid',
                               verbose_name='UserID, Name')  # Field name made lowercase.
    rollenname = models.ForeignKey('TblRollen', models.PROTECT, to_field='rollenname',
                                   db_column='rollenname')  # Field name made lowercase.
    schwerpunkt_vertretung = \
        models.CharField(db_column='schwerpunkt_vertretung',
                         max_length=100,
                         blank=True, null=True,
                         choices=SCHWERPUNKT_TYPE,
                         db_index=True
                         )  # Field name made lowercase. Field renamed to remove unsuitable characters.
    bemerkung = models.TextField(db_column='bemerkung', blank=True, null=True)  # Field name made lowercase.
    letzte_aenderung = models.DateTimeField(db_column='letzte_aenderung', default=timezone.now, blank=True,
                                            db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    userHatUserID_id = models.ForeignKey('UserHatTblUserIDundName_Transferiert', models.CASCADE,
                                         db_column='userHatUserID_id', default=None)  # Field name made lowercase.

    trans_afs = models.ManyToManyField(TblAfliste, through='TblRollehataf_Transferiert', default=None,
                                       related_name='trans_afs')
    on_transfer_list = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'tbl_UserHatRolle_Transferiert'
        verbose_name = "User und Ihre Rollen Transferiert"
        verbose_name_plural = "01_User und Ihre Rollen (tbl_UserHatRolle) Transferiert"
        ordering = ['userid__name', '-userid__userid', 'schwerpunkt_vertretung', 'rollenname', ]
        unique_together = (('userid', 'rollenname'),)

    def __str__(self) -> str:
        return str(self.userundrollenid)

    def get_rollenbeschreibung(self):
        return str(self.rollenname.rollenbeschreibung)

    get_rollenbeschreibung.short_description = 'Rollenbeschreibung'

    def get_absolute_url(self):
        # Returns the url for the whole list.
        return reverse('user_rolle_af', args=[])

    def get_absolute_update_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('user_rolle_af-update', args=[str(self.userundrollenid)])

    def get_absolute_create_url(self):
        # Returns the url to open the create-instance of the model (no ID given, the element does not exist yet).
        return reverse('user_rolle_af-create', args=[])

    def get_absolute_delete_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('user_rolle_af-delete', args=[str(self.userundrollenid)])
'''

# Die Tabelle enthält die Teambeschreibungen. Das eigentliche Team ist das Feld "team"
class TblOrga(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    team = models.CharField(db_column='team', unique=True, max_length=64, blank=False,
                            null=False, db_index=True)
    themeneigentuemer = models.CharField(db_column='themeneigentuemer', max_length=64, blank=False,
                                         null=False, db_index=True)

    class Meta:
        managed = True
        db_table = 'tblOrga'
        verbose_name = "Orga-Information"
        verbose_name_plural = "06_Organisations-Übersicht (tblOrga)"
        ordering = ['team']

    def __str__(self) -> str:
        return self.team

    def get_absolute_url(self):
        # Returns the url for the item.
        return reverse('teamliste', args=[])

    def get_absolute_update_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('team-update', args=[str(self.id)])

    def get_absolute_delete_url(self):
        # Returns the url to access a particular instance of the model.
        return reverse('team-delete', args=[str(self.id)])

    def get_absolute_create_url(self):
        # Returns the url to open the create-instance of the model (no ID given, the element does not exist yet).
        return reverse('team-create', args=[])


class UserHatTblUserIDundName(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    user_name = models.ForeignKey('User', db_column='username', on_delete=models.CASCADE)
    userid_name_id = models.ForeignKey('TblUserIDundName', db_column='userid_name_id', on_delete=models.CASCADE)
    rollen = models.ManyToManyField(to='TblAppliedRolle', related_name='applied_rollen', default=None, blank=True)
    delete_list = models.ManyToManyField(to='TblAppliedRolle', related_name='deleted_applied_rollen', default=None, blank=True)
    transfer_list = models.ManyToManyField(to='TblAppliedRolle', related_name='transfered_applied_rollen', default=None, blank=True)

'''
class UserHatTblUserIDundName_Geloescht(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    user_name = models.ForeignKey('User', db_column='username', on_delete=models.CASCADE)
    userid_name_id = models.ForeignKey('TblUserIDundName', db_column='userid_name_id', on_delete=models.CASCADE)
    del_rollen = models.ManyToManyField(TblRollen, through='TblUserhatrolle_Geloescht', default=None,
                                        related_name='del_rollen')
    on_delete_list = models.BooleanField(default=True)


class UserHatTblUserIDundName_Transferiert(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    user_name = models.ForeignKey('User', db_column='username', on_delete=models.CASCADE)
    userid_name_id = models.ForeignKey('TblUserIDundName', db_column='userid_name_id', on_delete=models.CASCADE)
    trans_rollen = models.ManyToManyField(TblRollen, through='TblUserhatrolle_Transferiert', default=None,
                                          related_name='trans_rollen')
    on_transfer_list = models.BooleanField(default=True)
'''

# Die Namen aller aktiven und gelöschten UserIDen und der dazugehörenden Namen (Realnamen und Technische User)
class TblUserIDundName(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    userid = models.CharField(db_column='userid', max_length=32, unique=True)  # Field name made lowercase.
    name = models.CharField(db_column='name', max_length=75, )  # Field name made lowercase.
    orga = models.ForeignKey('TblOrga', db_column='orga_id', on_delete=models.CASCADE, verbose_name='Team',
                             db_index=True)  # Field name made lowercase.
    zi_organisation = models.CharField(db_column='zi_organisation', max_length=64, verbose_name='ZI-Organisation',
                                       db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    geloescht = models.IntegerField(db_column='geloescht', blank=True, null=True, verbose_name='gelöscht',
                                    db_index=True)
    abteilung = models.CharField(db_column='abteilung', max_length=64, )  # Field name made lowercase.
    gruppe = models.CharField(db_column='gruppe', max_length=32, db_index=True)  # Field name made lowercase.
    rollen = models.ManyToManyField(TblRollen, related_name='applied_model_roles', through=TblUserhatrolle, default=None)

    class Meta:
        managed = True
        db_table = 'tblUserIDundName'
        index_together = (('gruppe', 'geloescht'),)
        verbose_name = "UserID-Name-Kombination"
        verbose_name_plural = "05_UserID-Name-Übersicht (tblUserIDundName)"
        ordering = ['geloescht', 'name', '-userid']
        unique_together = (('userid', 'name'),)
        index_together = (('geloescht', 'name', 'userid'),)

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

    colored_name.admin_order_field = 'name'
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


# Diese Funktion gehört inhaltlich zu tblUserIDundName, aber nicht in die Klasse (wird in form.py genutzt)
def hole_organisationen():
    # Liefert eine Liste an Tupeln mit Choices für die Orga-Auswahl zurück. Die Liste stammt aus tblUserIDundName.
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT zi_organisation FROM tblUserIDundName")
        rows = cursor.fetchall()
        return [('Bitte Organisation wählen', 'Bitte Organisation wählen')] + [(r[0], r[0]) for r in rows]


# Die verschiedenen technischne Plattformen (RACF, CICS, Unix, Win, AD, LDAP, test/Prod usw.)
class TblPlattform(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    tf_technische_plattform = models.CharField(db_column='tf_technische_plattform', unique=True, max_length=32,
                                               verbose_name='Plattform',
                                               db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    color = models.CharField(default="0", max_length=25, null=True)

    class Meta:
        managed = True
        db_table = 'tblPlattform'
        verbose_name = "Plattform"
        verbose_name_plural = "07_Plattform-Übersicht (tblPlattform)"
        ordering = ['tf_technische_plattform']

    def __str__(self) -> str:
        return self.tf_technische_plattform


# tblGesamtHistorie enthält alle Daten zu TFs in GFs in AFs für jeden User und seine UserIDen, wenn der User (mal) gelöscht wurde
class TblGesamtHistorie(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    id_alt = models.IntegerField(db_column='id_alt', blank=False, null=False,
                                 db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    userid_name = models.ForeignKey('TblUserIDundName', models.PROTECT, db_column='userid_und_name_id',
                                    to_field='id', )  # Field name made lowercase. Field renamed to remove unsuitable characters.

    tf = models.CharField(db_column='tf', max_length=100, verbose_name='TF')  # Field name made lowercase.
    tf_beschreibung = models.CharField(db_column='tf_beschreibung', max_length=300, blank=True, null=True,
                                       verbose_name='TF-Beschreibung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    enthalten_in_af = models.CharField(db_column='enthalten_in_af', max_length=100, blank=True, null=True,
                                       verbose_name='AF')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    modell = models.ForeignKey('TblUebersichtAfGfs', db_column='modell',
                               on_delete=models.CASCADE)  # Field name made lowercase.
    tf_kritikalitaet = models.CharField(db_column='tf_kritikalitaet', max_length=64, blank=True, null=True,
                                        verbose_name='TF-Kritikalität')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_eigentuemer_org = models.CharField(db_column='tf_eigentuemer_org', max_length=64, blank=True, null=True,
                                          verbose_name='TF-Eigentümer-orga')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    plattform = models.ForeignKey('TblPlattform', db_column='plattform_id', on_delete=models.CASCADE,
                                  verbose_name='Plattform')  # Field name made lowercase.
    gf = models.CharField(db_column='gf', max_length=100, blank=True, null=True,
                          verbose_name='GF')  # Field name made lowercase.
    vip_kennzeichen = models.CharField(db_column='vip', max_length=32, blank=True, null=True,
                                       verbose_name='VIP')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    zufallsgenerator = models.CharField(db_column='zufallsgenerator', max_length=32, blank=True, null=True,
                                        verbose_name='Zufallsgenerator')  # Field name made lowercase.

    datum = models.DateTimeField(db_column='datum', verbose_name='Recht gefunden am')  # Field name made lowercase.
    geloescht = models.IntegerField(db_column='geloescht', blank=True, null=True, verbose_name='gelöscht')
    gefunden = models.IntegerField(blank=True, null=True)
    wiedergefunden = models.DateTimeField(blank=True, null=True)
    geaendert = models.IntegerField(db_column='geaendert', blank=True, null=True,
                                    verbose_name='AF geändert')  # This field type is a guess.
    neueaf = models.CharField(db_column='neueaf', max_length=50, blank=True, null=True,
                              db_index=True)  # Field name made lowercase.
    loeschdatum = models.DateTimeField(db_column='loeschdatum', blank=True, null=True, verbose_name='Löschdatum')
    af_zuweisungsdatum = models.DateTimeField(db_column='af_zuweisungsdatum', blank=True, null=True,
                                              verbose_name='AF Zuweisung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    # ToDo: überlegen, ob af_zuweisungsdatum_alt weg kann oder wozu es genutzt werden soll
    af_zuweisungsdatum_alt = \
        models.DateTimeField(db_column='af_zuweisungsdatum_alt', blank=True, null=True,
                             verbose_name='AF Zuweisung alt')  # Field name made lowercase. Field renamed to remove unsuitable characters.

    af_gueltig_ab = models.DateTimeField(db_column='af_gueltig_ab', blank=True, null=True,
                                         verbose_name='AF gültig ab')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_gueltig_bis = models.DateTimeField(db_column='af_gueltig_bis', blank=True, null=True,
                                          verbose_name='AF gültig bis')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    direct_connect = models.CharField(db_column='direct_connect', max_length=100, blank=True, null=True,
                                      verbose_name='Direktverbindung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    hoechste_kritikalitaet_tf_in_af = \
        models.CharField(db_column='hk_tf_in_af', max_length=150, blank=True, null=True,
                         verbose_name='max. Krit. TF in AF')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gf_beschreibung = models.CharField(db_column='gf_beschreibung', max_length=300, blank=True, null=True,
                                       verbose_name='GF Kurzbeschreibung')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    nicht_ai = models.IntegerField(db_column='nicht_ai', blank=True,
                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    patchdatum = models.DateTimeField(db_column='patchdatum', blank=True, null=True, )  # Field name made lowercase.
    wertmodellvorpatch = models.TextField(db_column='wert_modell_vor_patch', blank=True,
                                          null=True)  # Field name made lowercase.
    letzte_aenderung = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tblGesamtHistorie'
        verbose_name = "Historisierter Eintrag der Gesamttabelle (tblGesamtHistorie)"
        verbose_name_plural = "99_Historisierte Einträge der Gesamttabelle (tblGesamtHistorie)"

    def __str__(self) -> str:
        return str(self.id)


###################################### Tblsubsysteme, Tblsachgebiete, TblDb2
# Ein paar Hilfstabellen.
# Die sind inhaltlich wahrscheinlich nicht super aktuell, helfen aber bei verschiedenen Fragen.
# Leider müssen die Modelle und ihre Columns so heißen, wie ihre Übreschriften es vorgeben (kein SQL-Standard)

class Tblsachgebiete(models.Model):
    sachgebiet = models.CharField(db_column='Sachgebiet', primary_key=True, max_length=32)  # Field name made lowercase.
    definition = models.CharField(db_column='Definition', max_length=250, blank=True,
                                  null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    verantwortlicher = models.CharField(db_column='Verantwortlicher', max_length=150, blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    telefon_verantwortlicher = models.CharField(db_column='Telefon', max_length=150, blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    user_id_verantwortlicher = models.CharField(db_column='user_id', max_length=50, blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    fk = models.CharField(db_column='Führungskraft', max_length=250, blank=True,
                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

    class Meta:
        managed = True
        db_table = 'tblSachgebiete'
        verbose_name = "Sachgebiet"
        verbose_name_plural = "97_Übersicht Sachgebiete (tbl_Sachgebiete)"
        ordering = ['sachgebiet']


class Tblsubsysteme(models.Model):
    sgss = models.CharField(db_column='sgss', primary_key=True, max_length=32)  # Field name made lowercase.
    definition = models.CharField(db_column='Definition', max_length=250, blank=True,
                                  null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    verantwortlicher = models.CharField(db_column='Verantwortlicher', max_length=150, blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    telefon_verantwortlicher = models.CharField(db_column='Telefon', max_length=150, blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    user_id_verantwortlicher = models.CharField(db_column='user_id', max_length=50, blank=True,
                                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    fk = models.CharField(db_column='Führungskraft', max_length=250, blank=True,
                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

    class Meta:
        managed = True
        db_table = 'tblSubsysteme'
        verbose_name = "Subsystem"
        verbose_name_plural = "96_Übersicht Subsysteme (tbl_Subsysteme)"
        ordering = ['sgss']


class TblDb2(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    source = models.CharField(db_column='source', max_length=8, default='none')  # Field name made lowercase.
    # grantee = models.ForeignKey('TblRacfGruppen', models.PROTECT, to_field='group', db_column='grantee')  # Field name made lowercase.
    grantee = models.CharField(db_column='grantee', max_length=15, default='none')  # Field name made lowercase.
    creator = models.CharField(db_column='CREATOR', max_length=15, default='none')  # Field name made lowercase.
    table = models.CharField(db_column='TABLE', max_length=31, db_index=True)  # Field name made lowercase.
    selectauth = models.CharField(db_column='SELECTAUTH', max_length=3, blank=True,
                                  null=True)  # Field name made lowercase.
    insertauth = models.CharField(db_column='INSERTAUTH', max_length=3, blank=True,
                                  null=True)  # Field name made lowercase.
    updateauth = models.CharField(db_column='UPDATEAUTH', max_length=3, blank=True,
                                  null=True)  # Field name made lowercase.
    deleteauth = models.CharField(db_column='DELETEAUTH', max_length=3, blank=True,
                                  null=True)  # Field name made lowercase.
    alterauth = models.CharField(db_column='ALTERAUTH', max_length=3, blank=True,
                                 null=True)  # Field name made lowercase.
    indexauth = models.CharField(db_column='INDEXAUTH', max_length=3, blank=True,
                                 null=True)  # Field name made lowercase.
    grantor = models.CharField(db_column='GRANTOR', max_length=15)  # Field name made lowercase.
    grantedts = models.CharField(db_column='GRANTEDTS', max_length=63)  # Field name made lowercase.
    datum = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tbl_DB2'
        verbose_name = 'DB2-Berechtigung'
        verbose_name_plural = '30_DB2 - Berechtigungen (Tbl_DB2)'
        ordering = ['id', ]

    def __str__(self) -> str:
        return str(self.id)


class TblRacfGruppen(models.Model):
    group = models.CharField(db_column='Group', primary_key=True, max_length=150)  # Field name made lowercase.
    test = models.IntegerField(db_column='Test', blank=True, null=True,
                               db_index=True)  # Field name made lowercase. This field type is a guess.
    produktion = models.IntegerField(db_column='Produktion', blank=True, null=True,
                                     db_index=True)  # Field name made lowercase. This field type is a guess.
    readonly = models.IntegerField(db_column='Readonly', blank=True, null=True,
                                   db_index=True)  # Field name made lowercase. This field type is a guess.
    db2_only = models.IntegerField(db_column='DB2-only', blank=True, null=True,
                                   db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. This field type is a guess.
    stempel = models.DateTimeField(db_column='Stempel', db_index=True)  # Field name made lowercase.

    def __str__(self) -> str:
        return str(self.group)

    class Meta:
        managed = True
        db_table = 'tbl_RACF_Gruppen'
        verbose_name = 'RACF-Berechtigung'
        verbose_name_plural = '40_RACF - Berechtigungen (tbl_DB2)'
        ordering = ['group', ]

    def get_test(self):
        return int(self.test)

    get_test.boolean = True
    get_test.admin_order_field = 'test'
    get_test.short_description = 'Test'

    def get_produktion(self):
        return int(self.produktion)

    get_produktion.boolean = True
    get_produktion.admin_order_field = 'produktion'
    get_produktion.short_description = 'Produktion'

    def get_readonly(self):
        return int(self.readonly)

    get_readonly.boolean = True
    get_readonly.admin_order_field = 'readonly'
    get_readonly.short_description = 'Read only'

    def get_db2_only(self):
        return int(self.db2_only)

    get_db2_only.boolean = True
    get_db2_only.admin_order_field = 'db2_only'
    get_db2_only.short_description = 'DB2 only'


###################################### Tblsubsysteme, Tblsachgebiete, TblDb2
# Tabellen für den Import neuer Listen
# Diese Tabellenspalten bleiben auf ihrem teilweise nicht SQL-konformem Namen,
# weil sie als Importspalten für die csv / xls-Datein benötigt werden.
# Gegebenenfalls kann das später noch angepasst werden.

class Tblrechteneuvonimport(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    identitaet = models.CharField(db_column='Identität', max_length=150, blank=False, null=False,
                                  db_index=True)  # Field name made lowercase.
    nachname = models.CharField(db_column='Nachname', max_length=150, blank=True,
                                null=True)  # Field name made lowercase.
    vorname = models.CharField(db_column='Vorname', max_length=150, blank=True, null=True)  # Field name made lowercase.
    tf_name = models.CharField(db_column='TF Name', max_length=100, blank=True,
                               null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_beschreibung = models.CharField(db_column='TF Beschreibung', max_length=250, blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_anzeigename = models.CharField(db_column='AF Anzeigename', max_length=100, blank=True,
                                      null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_beschreibung = models.CharField(db_column='AF Beschreibung', max_length=250, blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    hoechste_kritikalitaet_tf_in_af = models.CharField(db_column='Höchste Kritikalität TF in AF', max_length=150,
                                                       blank=True,
                                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_eigentuemer_org = models.CharField(db_column='TF Eigentümer Org', max_length=150, blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_applikation = models.CharField(db_column='TF Applikation', max_length=150, blank=True,
                                      null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_kritikalitaet = models.CharField(db_column='TF Kritikalität', max_length=150, blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gf_name = models.CharField(db_column='GF Name', max_length=150, blank=True,
                               null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gf_beschreibung = models.CharField(db_column='GF Beschreibung', max_length=250, blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    direct_connect = models.CharField(db_column='Direct Connect', max_length=150, blank=True,
                                      null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_zugewiesen_an_account_name = models.CharField(db_column='AF zugewiesen an Account-Name', max_length=150,
                                                     blank=True,
                                                     null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_gueltig_ab = models.DateTimeField(db_column='AF Gültig ab', blank=True,
                                         null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_gueltig_bis = models.DateTimeField(db_column='AF Gültig bis', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_zuweisungsdatum = models.DateTimeField(db_column='AF Zuweisungsdatum', blank=True,
                                              null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'tblRechteNeuVonImport'
        verbose_name = 'Importiere neue Daten (tblRechteNeuVonImport)'
        verbose_name_plural = 'Importiere neue Daten (tblRechteNeuVonImport)'
        ordering = ['id', ]


class Tblrechteamneu(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    userid = models.CharField(db_column='userid', max_length=50, blank=True, null=True,
                              db_index=True)  # Field name made lowercase.
    name = models.CharField(db_column='name', max_length=100, blank=True, null=True,
                            db_index=True)  # Field name made lowercase.
    tf = models.CharField(db_column='tf', max_length=100, blank=True, null=True,
                          db_index=True)  # Field name made lowercase.
    tf_beschreibung = models.CharField(db_column='tf_beschreibung', max_length=250, blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    enthalten_in_af = models.CharField(db_column='enthalten_in_af', max_length=100, blank=True, null=True,
                                       db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_kritikalitaet = models.CharField(db_column='tf_kritikalitaet', max_length=64, blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_eigentuemer_org = models.CharField(db_column='tf_eigentuemer_org', max_length=64, blank=True, null=True,
                                          db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_technische_plattform = \
        models.CharField(db_column='tf_technische_plattform', max_length=64, blank=True, null=True,
                         db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gf = models.CharField(db_column='gf', max_length=100, blank=True, null=True,
                          db_index=True)  # Field name made lowercase.
    vip_kennzeichen = models.CharField(db_column='vip', max_length=32, blank=True, null=True,
                                       db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    zufallsgenerator = models.CharField(db_column='zufallsgenerator', max_length=32, blank=True, null=True,
                                        db_index=True)  # Field name made lowercase.
    af_gueltig_ab = models.DateTimeField(db_column='af_gueltig_ab', blank=True,
                                         null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_gueltig_bis = models.DateTimeField(db_column='af_gueltig_bis', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    direct_connect = models.CharField(db_column='direct_connect', max_length=50, blank=True,
                                      null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    hoechste_kritikalitaet_tf_in_af = \
        models.CharField(db_column='hk_tf_in_af', max_length=150, blank=True, null=True,
                         db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gf_beschreibung = models.CharField(db_column='gf_beschreibung', max_length=250, blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_zuweisungsdatum = models.DateTimeField(db_column='af_zuweisungsdatum', blank=True,
                                              null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gefunden = models.IntegerField(db_column='gefunden', blank=True, null=True,
                                   db_index=True)  # Field name made lowercase.
    geaendert = models.IntegerField(db_column='geaendert', blank=True, null=True,
                                    db_index=True)  # Field name made lowercase.
    angehaengt_bekannt = models.IntegerField(db_column='angehaengt_bekannt', blank=True, null=True,
                                             db_index=True)  # Field name made lowercase.
    angehaengt_sonst = models.IntegerField(db_column='angehaengt_sonst', blank=True, null=True,
                                           db_index=True)  # Field name made lowercase.
    doppelerkennung = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tblRechteAMNeu'
        unique_together = (('userid', 'tf', 'enthalten_in_af', 'tf_technische_plattform', 'gf'),)


class Qryf3Rechteneuvonimportduplikatfrei(models.Model):
    userid = models.CharField(db_column='userid', max_length=32, blank=True, null=True,
                              db_index=True)  # Field name made lowercase.
    name = models.CharField(db_column='name', max_length=100, blank=True, null=True,
                            db_index=True)  # Field name made lowercase.
    tf = models.CharField(db_column='tf', max_length=100, blank=True, null=True,
                          db_index=True)  # Field name made lowercase.
    tf_beschreibung = models.CharField(db_column='tf_beschreibung', max_length=250, blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    enthalten_in_af = models.CharField(db_column='enthalten_in_af', max_length=100, blank=True, null=True,
                                       db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_kritikalitaet = models.CharField(db_column='tf_kritikalitaet', max_length=64, blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_eigentuemer_org = models.CharField(db_column='tf_eigentuemer_org', max_length=64, blank=True, null=True,
                                          db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tf_technische_plattform = \
        models.CharField(db_column='tf_technische_plattform', max_length=32, blank=True, null=True,
                         db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gf = models.CharField(db_column='gf', max_length=100, blank=True, null=True,
                          db_index=True)  # Field name made lowercase.
    vip_kennzeichen = models.CharField(db_column='vip', max_length=8, blank=True, null=True,
                                       db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    zufallsgenerator = models.CharField(db_column='zufallsgenerator', max_length=8, blank=True, null=True,
                                        db_index=True)  # Field name made lowercase.
    af_gueltig_ab = models.DateTimeField(db_column='af_gueltig_ab', blank=True,
                                         null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_gueltig_bis = models.DateTimeField(db_column='af_gueltig_bis', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    direct_connect = models.CharField(db_column='direct_connect', max_length=50, blank=True,
                                      null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    hoechste_kritikalitaet_tf_in_af = \
        models.CharField(db_column='hk_tf_in_af', max_length=150, blank=True, null=True,
                         db_index=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    gf_beschreibung = models.CharField(db_column='gf_beschreibung', max_length=250, blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    af_zuweisungsdatum = models.DateTimeField(db_column='af_zuweisungsdatum', blank=True,
                                              null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = True
        db_table = 'qryF3_RechteNeuVonImportDuplikatfrei'
        unique_together = (('userid', 'tf', 'enthalten_in_af', 'tf_technische_plattform', 'gf'),)


class RACF_Rechte(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    type = models.CharField(max_length=4, null=True)
    group = models.CharField(max_length=10, db_index=True)
    ressource_class = models.CharField(max_length=16, db_column='class', null=True)
    profil = models.CharField(max_length=128, db_index=True, null=True)
    access = models.CharField(max_length=16, null=True)
    test = models.IntegerField()
    produktion = models.IntegerField()
    alter_control_update = models.IntegerField()
    datum = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        managed = True
        verbose_name = 'RACF-Rechte'
        verbose_name_plural = '40_RACF - Berechtigungen'
        ordering = ['id', 'profil', ]

    def __str__(self) -> str:
        return str(self.id)


# Technische Abteilungsnummer;Organisation;Organisationsbezeichnung;Wirkende FK;Kostenstelle (wirkend);Org ID;
# Parent Organization;Parent Organization ID;Organization Type;FK-Name;Org Delegation Eigentümer-Genehmiger;Delegation FK-Genehmiger
# rv00458;ZI-AI-BA;Bestands-Anwendungen;XV13254;1001288;140329;ZI-AI;61901;OS0;Lutz Eichler;;

class Orga_details(models.Model):
    id = models.AutoField(primary_key=True)
    abteilungsnummer = models.CharField(max_length=32, null=True, db_index=True)
    organisation = models.CharField(max_length=100, db_index=True)
    orgaBezeichnung = models.CharField(max_length=100, null=True, db_index=True)
    fk = models.CharField(max_length=32, null=True, db_index=True)
    kostenstelle = models.CharField(max_length=32, null=True)
    orgID = models.IntegerField(null=True, db_index=True)
    parentOrga = models.CharField(max_length=32, null=True, db_index=True)
    parentOrgID = models.IntegerField(null=True)
    orgaTyp = models.CharField(max_length=32, null=True)
    fkName = models.CharField(max_length=32, null=True)
    delegationEigentuemer = models.CharField(max_length=32, null=True)
    delegationFK = models.CharField(max_length=32, null=True)
    datum = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        managed = True
        verbose_name = 'Orga-Details'
        verbose_name_plural = '50_Orga - Details'
        ordering = ['id', 'organisation', 'orgID', 'parentOrga', 'fkName', ]

    def __str__(self) -> str:
        return str(self.id)


# Versionshistorie der Daten-Importe; Darüber ist auch ein aktuell laufender Import feststellbar
# Die beiden Felder max und aktuell dienen dem Anzeigen eins Fortschrittbalkens
class Letzter_import(models.Model):
    id = models.AutoField(primary_key=True)
    start = models.DateTimeField(null=False)
    user = models.CharField(max_length=100, null=True)
    end = models.DateTimeField(null=True)
    max = models.IntegerField(null=False)
    aktuell = models.IntegerField(null=False)
    schritt = models.IntegerField(null=False, default=1)

    class Meta:
        managed = True
        verbose_name = 'Letzter Import'
        verbose_name_plural = 'Letzte Importe'
        ordering = ['id', 'start', 'end']


class Modellierung(models.Model):
    """
	Tabelle aus dem Export für die TF-Rezertifizierung.
	Die Daten enthalten alle aktuellen Modellierungen einer TF in die GFs und AFs

	Das kann dem späteren Erzeugen von Mails dienen, um User auf Möglichekiten hinzuweisen,
	sich von Direct Connects zu trennen.
	"""
    entitlement = models.CharField(max_length=50, null=True, db_index=True)
    neue_beschreibung = models.CharField(max_length=500, null=True)
    plattform = models.CharField(max_length=30, null=True, db_index=True)
    gf = models.CharField(max_length=50, null=False, db_index=True)
    beschreibung_der_gf = models.CharField(max_length=500, null=True)
    af = models.CharField(max_length=50, null=False, db_index=True)
    beschreibung_der_af = models.CharField(max_length=500, null=True)
    organisation_der_af = models.CharField(max_length=100, null=True)
    eigentuemer_der_af = models.CharField(max_length=100, null=True)
    aus_modellierung_entfernen = models.CharField(max_length=100, null=True)
    datei = models.CharField(max_length=100, null=True)
    letzte_aenderung = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        managed = True
        verbose_name = 'Modellierung AF GF TF'
        verbose_name_plural = '60_Modellierung AF GF TF'
    # ordering = [ 'id', 'organisation', 'orgID', 'parentOrga', 'fkName', ]


class Direktverbindungen(models.Model):
    """
	Tabelle aus dem Export für die TF-Rezertifizierung.
	Die Daten enthalten alle derzeit bekannten Direktverbindungen zu TFs der Abteilung.

	Auch das kann dem späteren Erzeugen von Mails dienen, um User auf Möglichekiten hinzuweisen,
	sich von Direct Connects zu trennen.
	Diese Tabelle muss geeignet mit der Tabelle Modellierung verknüpft werden
	"""
    organisation = models.CharField(max_length=30, null=False)
    entscheidung = models.CharField(max_length=30, null=True)
    entitlement = models.CharField(max_length=100, null=False, db_index=True)
    applikation = models.CharField(max_length=20, null=True)
    instanz = models.CharField(max_length=20, null=True)
    identitaet = models.CharField(max_length=50, null=False, db_index=True)
    manager = models.CharField(max_length=100, null=True)
    vorname = models.CharField(max_length=100, null=False)
    nachname = models.CharField(max_length=100, null=False)
    account_name = models.CharField(max_length=50, null=False)
    status = models.CharField(max_length=100, null=True)
    typ = models.CharField(max_length=100, null=True)
    nicht_anmailen = models.CharField(max_length=8, null=True)
    ansprechpartner = models.CharField(max_length=100, null=True)
    letzte_aenderung = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        managed = True
        verbose_name = 'Direktverbindungen'
        verbose_name_plural = '61_Direktverbindungen'
        unique_together = (('entitlement', 'account_name'),)


class CustomAccountManager(BaseUserManager):
    def create_user(self, username, email, password):
        user = self.model(username=username, email=email, password=password)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self.db)
        return user

    def create_staff(self, username, email, password):
        user = self.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_superuser = False
        user.save(using=self.db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username=username, email=email, password=password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)
        return user

    def get_by_natural_key(self, identity_):
        case_insensitive_identitiy_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        print(identity_)
        return self.get(**{case_insensitive_identitiy_field: identity_})


class User(AbstractUser):
    class Meta:
        managed = True
        db_table = 'auth_user'

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    last_login = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    userid_name = models.ManyToManyField(TblUserIDundName, default=None, related_name="user_rights",
                                         through=UserHatTblUserIDundName)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    deleted = models.BooleanField(default=False)
    last_rights_update = models.DateTimeField(editable=True, null=True, blank=True, default=None)
    #transfer_list = models.ManyToManyField(TblUserIDundName, default=None, related_name="transfer_list",
    #                                       through=UserHatTblUserIDundName_Transferiert)
    #delete_list = models.ManyToManyField(TblUserIDundName, default=None, related_name="delete_list",
    #                                     through=UserHatTblUserIDundName_Geloescht)

    # identity = models.CharField(max_length=7, unique=True)
    # avatar = models.ImageField()

    # orga = djongomodels.EmbeddedModelField(model_container=Orga)
    # department = djongomodels.EmbeddedModelField(model_container=Department)
    # group = djongomodels.EmbeddedModelField(model_container=Group)
    # zi_organisation = djongomodels.EmbeddedModelField(model_container=ZI_Organisation)
    # roles = djongomodels.ArrayReferenceField(to=Role)
    # direct_connect_afs = djongomodels.ArrayReferenceField(to=AF)
    # direct_connect_gfs = djongomodels.ArrayReferenceField(to=GF)
    # direct_connect_tfs = djongomodels.ArrayReferenceField(to=TF)
    # my_requests = djongomodels.ArrayReferenceField(to=ChangeRequests, on_delete=models.CASCADE)
    # user_afs = djongomodels.ArrayModelField(model_container=User_AF)

    objects = CustomAccountManager()

    def natural_key(self):
        return self.username

    def __str__(self):
        return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
