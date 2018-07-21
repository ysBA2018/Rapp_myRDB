from django.contrib.auth.models import User
from .models import TblGesamt, TblOrga, TblUserIDundName, TblUebersichtAfGfs, TblPlattform

import django_filters

class keinUserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', ]

class PanelFilter(django_filters.FilterSet):
    class Meta:
        model = TblGesamt
        fields = ['tf', 'enthalten_in_af', 'plattform', 'gf', 'geloescht', ]

