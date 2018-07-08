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
admin.site.register(TblGesamt)
admin.site.register(TblOrga)

# Zeige einen Eintrag der Orga-Tabelle zeilenweise an


class OrgaInline(admin.TabularInline):
	model = TblOrga
	extra = 1


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

	site_header = "Tralli und trallala"


admin.site.register(TblUserIDundName, UserIDundNameAdmin)

