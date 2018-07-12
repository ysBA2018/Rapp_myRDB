# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

def rapp(request):
    return render(request, "index.html")

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from django.utils import timezone
from rapp.models import TblUserIDundName, TblGesamt

class IndexView(generic.ListView):
	template_name = 'rapp/index.html'
	context_object_name = 'first_list'

	def get_queryset(self):
		"""
		Liefere nur diejenigen User-Einträge, die nicht gelöscht sind
		"""
		return TblUserIDundName.objects.filter(
			geloescht = False,
		) # .order_by('name')[:40]


class IndexView(generic.ListView):
	template_name = 'rapp/index.html'
	context_object_name = 'first_list'

	model = TblGesamt

	def get_queryset(self):
		return TblGesamt.objects.filter(geloescht != True) # Liefere nur nicht gelöschte Einträge

