from django.contrib.auth.models import User, Group
from .models import TblGesamt, TblOrga, TblUserIDundName, TblUebersichtAfGfs, TblPlattform

import django_filters
from django import forms

"""
class UserFilter(django_filters.FilterSet):
	# first_name = django_filters.CharFilter(lookup_expr='icontains')
	# year_joined = django_filters.NumberFilter(field_name='date_joined', lookup_expr='year')
	class Meta:
		model = User
		fields = {
			'username': ['exact', ],
			'first_name': ['icontains', ],
			'last_name': ['exact', ],
			'date_joined': ['year', 'year__gt', 'year__lt', ],
		}
		# fields = ['username', 'first_name', 'last_name', ]

"""

class UserFilter(django_filters.FilterSet):
	first_name = django_filters.CharFilter(lookup_expr='icontains')
	year_joined = django_filters.NumberFilter(field_name='date_joined', lookup_expr='year')
	groups = django_filters.ModelMultipleChoiceFilter(queryset=Group.objects.all(),
													  widget=forms.CheckboxSelectMultiple)
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'year_joined', 'groups']


class UserIDFilter(django_filters.FilterSet):
	userid = django_filters.CharFilter(lookup_expr='istartswith')
	name = django_filters.CharFilter(lookup_expr='icontains')
	geloescht = django_filters.BooleanFilter(lookup_expr='exact')

	class Meta:
		model = TblUserIDundName
		fields = '__all__'



class PanelFilter(django_filters.FilterSet):
	tf = django_filters.CharFilter(lookup_expr='icontains')
	enthalten_in_af = django_filters.CharFilter(lookup_expr='icontains')
	userid_name__userID = django_filters.CharFilter(lookup_expr='istartswith')
	plattform = django_filters.BooleanFilter(lookup_expr='exact')
	geloescht = django_filters.BooleanFilter(lookup_expr='exact')

	class Meta:
		model = TblUserIDundName
		fields = '__all__'


