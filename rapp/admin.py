# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

# from .models import Bastel, TblAflisteZiaiba, TblCicsdetails, TblDb2
# from .models import TblGesamtKomplett, Tblp0Gesamt, Tblgesamthistorie

from rapp.models import TblUebersichtAfGfs, TblUserIDundName, TblOrga, TblPlattform, TblGesamt
	# TblUserhatrolle, TblRollen, TblRollehataf

admin.site.register(TblUebersichtAfGfs)
admin.site.register(TblPlattform)
#admin.site.register(TblUserIDundName)
# admin.site.register(TblUserhatrolle)
# admin.site.register(TblRollen)
# admin.site.register(TblRollehataf)
# admin.site.register(TblOrga)

# Zeige einen Eintrag der Orga-Tabelle zeilenweise an


# ######################################################################################################
# tbl Gesamt
# ######################################################################################################

@admin.register(TblGesamt)
class Gesamt(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True

	fieldsets = [
		('Standard-Informationen', {'fields': ['userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'modell',
												'plattform', 'gf', 'af_gueltig_bis', 'direct_connect',
												'af_zuweisungsdatum', 'datum', 'geloescht',]}),
		('Detail-Informationen  ', {'fields': ['tf_kritikalitaet', 'tf_eigentuemer_org', 'vip_kennzeichen', 'zufallsgenerator',
												'af_gueltig_ab', 'hoechste_kritikalitaet_tf_in_af', 'gf_beschreibung',
												'gefunden', 'wiedergefunden', 'geaendert', 'neueaf', 'nicht_ai',
												'patchdatum', 'wertmodellvorpatch', 'loeschdatum'], 'classes': ['collapse']}),
	]
	list_display = ('id', 'userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'gf',
		'plattform', 'get_direct_connect', 'get_active',
	)
	list_filter = ('geloescht', 'direct_connect', 'userid_name__gruppe', 'plattform', )
	list_display_links = ('id', )
	list_editable = ('tf', 'tf_beschreibung', 'enthalten_in_af', 'plattform', 'gf', )
	# search_fields = ['userid_name', 'tf', 'tf_beschreibung', 'enthalten_in_af', 'plattform', 'gf']
	search_fields = ['userid_name__name', 'tf',
					 # 'tf_beschreibung', 'enthalten_in_af', 'plattform', 'gf',
					]

# Inline function to show all Instances of Gesamt in UserIDundNameView or UebersichtAFGFs
class GesamtInline(admin.TabularInline):
	model = TblGesamt
	extra = 0


# ######################################################################################################
# tbl UserIDundName
# ######################################################################################################

@admin.register(TblUserIDundName)
class UserIDundNameAdmin(admin.ModelAdmin):

	fieldsets = [
		('User-Informationen', {'fields': ['userid', 'name', 'orga', 'geloescht']}),
		('Orga-Details      ', {'fields': ['zi_organisation', 'abteilung', 'gruppe'], 'classes': ['collapse']}),
	]
	# inlines = [OrgaInline]

	list_display = ('id', 'userid', 'colored_name', 'orga', 'zi_organisation', 'get_active', 'abteilung', 'gruppe',)
	list_display_links = ('userid', 'colored_name', 'get_active', )
	list_editable = ('orga', 'zi_organisation', 'abteilung', 'gruppe', )
	search_fields = ['name', 'zi_organisation', 'abteilung', 'gruppe', 'userid']

	list_filter = ('geloescht', 'abteilung', 'gruppe', 'orga', )

	actions_on_top = True
	actions_on_bottom = True

	# Nice idea, but VERY slow
	inlines = [GesamtInline]


# Inline function to show all Instances of UserIDundName in OrgaView
class UserIDundNameInline(admin.TabularInline):
	model = TblUserIDundName
	extra = 0



# ######################################################################################################
# tbl Orga
# ######################################################################################################

@admin.register(TblOrga)
class Orga(admin.ModelAdmin):
	actions_on_top = True
	actions_on_bottom = True
	list_display = ('team', 'themeneigentuemer', )
	list_filter = ('themeneigentuemer', )
	list_display_links = ('team', )
	list_editable = ('themeneigentuemer', )
	search_fields = ['team',]

	inlines = [UserIDundNameInline]



# ######################################################################################################
# tbl Orga
# ######################################################################################################

# @admin.register(TblOrga)
