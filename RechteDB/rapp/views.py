# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
# Zum Einlesen der Versionsnummer
import os
import re
import subprocess
import sys
# Imports für die Selektions-Views panel, selektion u.a.
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from math import *

from .filters import PanelFilter
from .models import TblUserIDundName, TblGesamt, TblOrga, TblPlattform, Letzter_import  # ToDo LetzterImport raus hier
# An dieser stelle stehen diverse Tools zum Aufsetzen der Datenbank mit SPs
from .stored_procedures import finde_procs_exakt, connection


###################################################################
# RApp - erforderliche Sichten und Reports

# ToDo: Abgleich vorhandener Rechte selektierter User mit Zertifizierungsliste (Importfunktion für die Liste!)

# ToDo: Welche Direktzuordnungen hat eine UID schon über vorhandene AF?
# ToDo: - Welche Zuordnung ist damit doppelt?
# ToDo: - Welche TF fehlt als zugeordnete AF?
# ToDo: - Welche bekannten AFen würden hier helfen?

# ToDo: Importfunktion für "Alle meine TFen und die zugeordneten User"
# ToDo: Importfunktion für "Alle meine AFen und die zugeordneten User"

# ToDo: Alten "Finde Datei"-Dialog implemenieren

# ToDo: Hier werden sicherlich noch etliche Filterfunktionen benötigt:
# ToDo: Was passt eventuell nicht (welche Personen passen nicht in die erlaubten Orgabereiche)
# ToDo: Welche Rechte haben Ausschluss-/Einschlusskriterien und sind sie erfüllt?
# ToDo: Welche Rechte sind redundant, weil sie neu modelliert wurden und was ist die Alternativempfehlung?
# ToDo: Zu welchen Orgabereichen (Importfunktion dafür!) gehören die identifizierten User (Vorbereitung Mail an FK zum Prüfen und eventuellem Löschen

# ToDo: Die gesamten Modellnamen können mal überarbeitet werden (kein TBL am Anfang etc.)

# ToDo: Checken, ob tbl_Gesamt_komplett irgendwo noch als Gesamttabelle aller userids benötigt wird, sonst in SP löschen nach Nutzung

# ToDo: Neuanlage von Rollen in mehreren Zeilen vorbereiten?
# ToDo: Suche: Wo kann man die Modelle anpassen? Braucht das Ändern der Modellzugehörigkeit noch jemand, oder ist das mit dem neuen Rollenmodell obsolet?
# ToDo: Userrolle: Link von der Rollensicht auf tbluseridundname im Admin

from django.contrib.auth import get_user_model
User = get_user_model()

def get_version(package):
	"""
	Return package version as listed in `__version__` in `init.py`.
	"""
	init_py = open(os.path.join(package, '__init__.py')).read()
	manual = re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)
	git_rev = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
	return manual + ' - ' + git_rev.decode('utf-8')
version = get_version('rapp')

def initialisiere_AFliste():
	'''
	Aufbau der tbl_AFListe; Deren Inhalt ist abhängig von Veränderungen in tblUebersichtAF_GFs

	:return: nichts
	'''
	with connection.cursor() as cursor:
		try:
			cursor.callproc("erzeuge_af_liste")  # diese SProc benötigt die Orga nicht als Parameter
		except:
			e = sys.exc_info()[0]
			fehler = 'Fehler in initialisiere_AFliste(): {}'.format(e)
			print('Fehler Beim Erstellen der AFListe, StoredProc erzeuge_af_liste', fehler)
		cursor.close()

# Der Direkteinsteig für die gesamte Anwendung
# Dies ist die Einstiegsseite, sie ist ohne Login erreichbar.
def home(request):
	"""
	Zeige ein paar Statistik-Infos über die RechteDB.
	Das stellt sicher, dass die Anbidnung an die Datenbank funzt
	:param request: GET oder POST Request vom Browser
	:return: Gerendertes HTML
	"""
	num_rights = TblGesamt.objects.all().count()
	num_userids = TblUserIDundName.objects.all().count
	num_active_userids = TblUserIDundName.objects.filter(geloescht=False).count
	num_plattforms = TblPlattform.objects.count
	num_iamba = TblGesamt.objects.filter(geloescht=False,
										 userid_name__abteilung__icontains='ZI-AI-BA',
										 userid_name__geloescht=False).count
	num_userids_in_department = TblUserIDundName.objects.filter(geloescht=False, abteilung__icontains='ZI-AI-BA').count
	num_teams = TblOrga.objects.all().count
	num_active_rights = TblGesamt.objects.filter(geloescht=False).count
	stored_procedures = finde_procs_exakt()

	try:
		letzter_import_im_modell = Letzter_import.objects.latest('id')
		letzter_import = str(letzter_import_im_modell.end)[:19]
	except:
		letzter_import = 'unbekannt'

	# Sicherheitshalber wird immer bei Aufruf der Startseite die Tabelle tbl_AFListe neu aufgebaut
	initialisiere_AFliste()

	request.session['version'] = version
	return render(
		request,
		'index.html',
		context={
			'num_rights': num_rights,
			'num_active_rights': num_active_rights,
			'num_userIDs': num_userids,
			'num_iam_ba': num_iamba,
			'num_activeUserIDs': num_active_userids,
			'num_plattforms': num_plattforms,
			'num_userIDsInDepartment': num_userids_in_department,
			'num_teams': num_teams,
			'num_users': User.objects.all().count,
			'sps': stored_procedures,
			'letzter_import': letzter_import,
		},
	)

###################################################################
# Gesamtliste
class GesamtListView(ListView):
	"""Die Gesamtliste der Rechte ungefiltert"""
	model = TblGesamt
	paginate_by = 50

class GesamtDetailView(generic.DetailView):
	"""Die Detailsicht eines einzelnen Rechts"""
	model = TblGesamt


###################################################################
# Rechte-User (Gemeint sind nicht die Anwender der RechteDB!)
class UserIDundNameListView(ListView):
	"""Die Gesamtliste der User ungefiltert"""
	model = TblUserIDundName
	paginate_by = 50
class TblUserIDundNameCreate(CreateView):
	"""Erstellen eines neuen Users"""
	model = TblUserIDundName
	fields = '__all__'
	initial = {'geloscht' : 'False',}
class TblUserIDundNameUpdate(UpdateView):
	"""Ändern eines Users"""
	model = TblUserIDundName
	fields = '__all__'
class TblUserIDundNameDelete(DeleteView):
	"""Löschen eines Users"""
	model = TblUserIDundName
	success_url = reverse_lazy('userliste')

def userToggleGeloescht(request, pk):
	"""
	View function zum Togglen des Gelöscht-Flags in der DB für eine konkrete Instanz.
	Dieser Aufruf wird nicht in zwei Schritten als GET / POST-Kombination durchgeführt.
	sondern ausschließlich als GET.
	:param request: GET oder POST Request vom Browser
	:param pk: ID des zu löschenden UserID-Eintrags
	:return: Gerendertes HTML
	"""
	user_inst = get_object_or_404(TblUserIDundName, pk = pk)

	user_inst.geloescht = not user_inst.geloescht
	user_inst.save()

	# redirect to a new URL:
	return HttpResponseRedirect(reverse('userliste') )

###################################################################
# Die Gesamtliste der Teams (TblOrga)
class TeamListView(generic.ListView):
	"""Die Gesamtliste der Teams (TblOrga)"""
	model = TblOrga

class TblOrgaCreate(CreateView):
	"""Neues Team erstellen"""
	model = TblOrga
	fields = '__all__'
	initial = {'geloscht' : 'False',}
class TblOrgaUpdate(UpdateView):
	"""Team ändern"""
	model = TblOrga
	fields = '__all__'
class TblOrgaDelete(DeleteView):
	"""Team löschen"""
	model = TblOrga
	success_url = reverse_lazy('teamliste')

# Paginierung nach Tutorial - Aufteilung langer Seiten in mehrere
def pagination(request, liste, psize=20):
	pagesize = request.GET.get('pagesize')
	if type(pagesize) == type(None) or pagesize == '' or int(pagesize) < 1:
		pagesize = psize  # default, kann man von außen übersteuern
	else:
		pagesize = int(pagesize)
	paginator = Paginator(liste, pagesize)
	page = request.GET.get('page', 1)
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return (paginator, pages, pagesize)

###################################################################
# Panel geht direkt auf die Gesamt-Datentabelle
def panel(request):
	"""
	# Filter-Panel zum Selektieren aus der Gesamttabelle nach allen möglichen Kriterien
	# Beachtet werden die relevanten Foreign Keys
	:param request: GET oder POST Request vom Browser
	:return: Gerendertes HTML
	"""
	panel_list = TblGesamt.objects.all()
	panel_filter = PanelFilter(request.GET, queryset=panel_list)
	panel_list = panel_filter.qs

	(paginator, pages, pagesize) = pagination(request, panel_list)
	context = {
		'paginator': paginator,
		'filter': panel_filter,
		'pages': pages,
		'meineTabelle': panel_list,
		'pagesize': pagesize,
		'gesamtzahl': panel_list.count()
	}
	return render(request, 'rapp/panel_list.html', context)


###################################################################
# Panel_UhR betrachtet den Soll-Zustand über UserHatRolle

def panelDownload(request):
	"""
	Exportfunktion für das Filter-Panel zum Selektieren aus der Gesamttabelle (s. panel()).
	:param request: GET oder POST Request vom Browser
	:return: Gerendertes HTML
	"""
	panel_list = TblGesamt.objects.all()
	panel_filter = PanelFilter(request.GET, queryset=panel_list)
	panel_list = panel_filter.qs

	(paginator, pages, pagesize) = pagination(request, panel_list, 100000)
	context = {
		'paginator': paginator,
		'filter': panel_filter,
		'pages': pages,
		'meineTabelle': panel_list,
		'pagesize': pagesize,
	}
	f = PanelFilter(request.GET, queryset=TblGesamt.objects.all())

	response = HttpResponse(content_type="text/csv")
	response['Content-Disposition'] = 'attachment; filename="gesamt.csv"' # ToDo Hänge Datum an Dateinamen an

	writer = csv.writer(response, delimiter = ';', quotechar = '"')
	writer.writerow([
		'tf', 'tf_beschreibung',
		'enthalten_in_af',
		'name', 'userid', 'team',
		'name_af_neu', 'name_gf_neu'
	])

	for obj in pages:
		writer.writerow([
			obj.tf, obj.tf_beschreibung,
			obj.enthalten_in_af,
			obj.userid_name.name, obj.userid_name.userid, obj.userid_name.zi_organisation,
			obj.modell.name_af_neu, obj.modell.name_gf_neu
		])

	return response

def magic_click(request):
	'''
	Ist nur eine Hülle, um Funktionen aufrufen zu können, die noch über keine Seite verfügen.
	:param request:
	:return:
	'''
	findeNeueAFGF('rva_00763_web_entwickler')
	return home(request)


def findeNeueAFGF(gesuchte_af):
	'''
	Finde alle AF/GF-Kombinationen zu einer AF in der Tabelle der erlaubten Kombinationen
	Das wird am Anfang benötigt für den Fall, dass nur einzelne Teilkombinationen fehlen
	Anschließend muss die AF_Liste gegebenenfalls ergänzt werden.

	:param gesuchte_af: String mit der AF, zu der ggfs. die AF/GF-Kombinationen gesucht und ergänzt werden sollen.
	:return: None oder Fehlerstring
	'''

	sql = '''
		INSERT INTO `tblUEbersichtAF_GFs`
			(`name_gf_neu`, `name_af_neu`, `kommentar`, `zielperson`, geloescht, `modelliert`)
		
			SELECT 	`gf` as name_gf_neu,
				`enthalten_in_af` as name_af_neu,
				'Automatisch ergänzt' as kommentar,
				'Alle' as zielperson,
				0 as geloescht,
				now() as modelliert
			FROM `tblGesamt`
			WHERE `enthalten_in_af` = \'{}\'
				AND NOT geloescht = true
			GROUP BY `enthalten_in_af`, `gf`
		
		ON DUPLICATE KEY UPDATE
			`modelliert` = now(),
			geloescht = 0;	
	'''.format(gesuchte_af)

	with connection.cursor() as cursor:
		try:
			cursor.execute (sql)
		except:
			e = sys.exc_info()[0]
			fehler = 'Error in push_sp(): {}'.format(e)
			return fehler
		cursor.close()


	with connection.cursor() as cursor:
		try:
			cursor.callproc("erzeuge_af_liste")  # diese SProc benötigt die Orga nicht als Parameter
		except:
			e = sys.exc_info()[0]
			fehler = 'Fehler in findeNeueAFGF(): {}'.format(e)
			print('Fehler Beim Erstellen der AFListe, StoredProc erzeuge_af_liste', fehler)
			return fehler
		cursor.close()
	return None

