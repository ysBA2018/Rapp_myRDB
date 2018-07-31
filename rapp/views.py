# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.

from django.shortcuts import get_object_or_404
from rapp.models import TblUserIDundName, TblGesamt, TblOrga, TblPlattform
from django.views import generic, View

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .filters import UserFilter

# Imports für die Selektions-Views panel, slektion u.a.
from django.contrib.auth.models import User
from django.shortcuts import render
# from .filters import UserFilter
from .filters import PanelFilter
from django.core.paginator import Paginator


###################################################################
# Die Einstiegsseite
class IndexView(View):
	def get(self, request):

		# Zeige ein paar Statistik-Infos über die RechteDB.
		# Das stellt sicher, dass die Anbidnung an die Datenbank funzt
		num_rights = TblGesamt.objects.all().count()
		num_userids = TblUserIDundName.objects.all().count
		num_active_userids = TblUserIDundName.objects.filter(geloescht=False).count
		num_plattforms = TblPlattform.objects.count
		num_userids_in_department = TblUserIDundName.objects.filter(geloescht=False, abteilung__icontains='ZI-AI-BA').count
		num_teams = TblOrga.objects.all().count

		return HttpResponse(
			render(
				request,
				'index.html',
				context={'num_rights': num_rights,  # Todo: Korrekte Daten einpflegen
						 'num_userIDs': num_userids,
						 'num_activeUserIDs': num_active_userids,
						 'num_plattforms': num_plattforms,
						 'num_userIDsInDepartment': num_userids_in_department,
						 'num_teams': num_teams,
						 'num_users': User.objects.all().count,
						 },
			)
		)



###################################################################
# Die Gesamtliste der Rechte ungefiltert
class GesamtListView(generic.ListView):
	model = TblGesamt
	paginate_by = 100

# Die Detailsicht eines einzelnen Rechts
class GesamtDetailView(generic.DetailView):
	model = TblGesamt

# Die Gesamtliste der Abteilung BA
class BaListView(generic.ListView):
	context_object_name = 'ba_list'
	template_name = 'rapp/ba_list.html'		# ToDo: Das ist ja blöd, dass der Pfad angegeben werden muss
	queryset = TblGesamt.objects.filter(userid_name__geloescht=False).filter(userid_name__abteilung='ZI-AI-BA').filter(geloescht=False)
	# paginate_by = 50



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

###################################################################
# Die Ab hier kommen die Views für das Panel


###################################################################
# Nur zum Zeigen, wie das mit den Panels gehen könnte....

def search(request):
	user_list = User.objects.all()
	user_filter = UserFilter(request.GET, queryset=user_list)
	return render(request, 'rapp/user_list.html', {'filter': user_filter})


###################################################################
# Panel geht direkt auf die Gesamt Datentabelle

def panel(request):
	panel_list = TblGesamt.objects.all()
	# panel_list = TblUserIDundName.objects.all()
	panel_filter = PanelFilter(request.GET, queryset=panel_list)
	panel_list = panel_filter.qs

	paginator = Paginator(panel_list, 10)
	page = request.GET.get('page', 1)
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	args = {'paginator': paginator, 'filter': panel_filter, 'pages': pages, 'meineTabelle': panel_list}
	return render(request, 'rapp/panel_list.html', args)

