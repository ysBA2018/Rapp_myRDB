# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.

from django.shortcuts import get_object_or_404, render
from rapp.models import TblUserIDundName, TblGesamt, TblOrga
from django.views import generic

from django.http import HttpResponseRedirect
from django.urls import reverse


def index(request):
	"""
	View function for home page of site.

	Zeige ein paar Statistik-Infos über die RechteDB.
	Das stellt sicher, dass die Anbidnung an die Datenbank funzt

	# Render the HTML template index.html with the data in the context variable
	"""
	num_rights = TblGesamt.objects.all().count()
	num_userids = TblUserIDundName.objects.all().count
	num_active_userids = TblUserIDundName.objects.filter(geloescht=False).count
	num_userids_in_department = TblUserIDundName.objects.filter(geloescht=False, abteilung__icontains='ZI-AI-BA').count
	num_teams = TblOrga.objects.all().count

	return render(
		request,
		'index.html',
		context={'num_rights': num_rights,  # Todo: Korrekte Daten einpflegen
				 'num_userIDs': num_userids,
				 'num_activeUserIDs': num_active_userids,
				 'num_userIDsInDepartment': num_userids_in_department,
				 'num_teams': num_teams,
				 'num_users': 23,
		},
	)



# Die Gesamtliste der Rechte ungefiltert
class GesamtListView(generic.ListView):
	model = TblGesamt
	paginate_by = 100

# Die Detailsicht eines einzelnen Rechts
class GesamtDetailView(generic.DetailView):
	model = TblGesamt

###################################################################
# Die Gesamtliste der User ungefiltert
class UserIDundNameListView(generic.ListView):
	model = TblUserIDundName
	paginate_by = 100

# Die Detailsicht eines einzelnen Users
# class UserIDundNameDetailView(generic.DetailView):
#	model = TblUserIDundName


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class TblUserIDundNameCreate(CreateView):
	model = TblUserIDundName
	fields = '__all__'
	initial = {'geloscht' : 'False',}

class TblUserIDundNameUpdate(UpdateView):
	model = TblUserIDundName
	fields = '__all__'

class TblUserIDundNameDelete(DeleteView):
	model = TblUserIDundName
	success_url = reverse_lazy('userliste')

def userToggleGeloescht(request, pk):
	# View function zum Togglen des Gelöscht-Flags in der DB für eine konkrete Instanz.
	# Dieser Aufruf wird nicht in zwei Schritten als GET / POST-Kombination durchgeführt.
	# sondern ausschließlich als GET.
	user_inst = get_object_or_404(TblUserIDundName, pk = pk)

	user_inst.geloescht = not user_inst.geloescht
	user_inst.save()

	# redirect to a new URL:
	return HttpResponseRedirect(reverse('userliste') )

###################################################################
# Die Gesamtliste der Teams (TblOrga)

class TeamListView(generic.ListView):
	model = TblOrga
	# paginate_by = 100

class TblOrgaCreate(CreateView):
	model = TblOrga
	fields = '__all__'
	initial = {'geloscht' : 'False',}

class TblOrgaUpdate(UpdateView):
	model = TblOrga
	fields = '__all__'

class TblOrgaDelete(DeleteView):
	model = TblOrga
	success_url = reverse_lazy('teamliste')

