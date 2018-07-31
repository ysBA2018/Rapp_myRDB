import django_tables2 as tables
from .models import TblGesamt

class PanelTable(tables.Table):
    class Meta:
        model = TblGesamt
        template_name = 'django_tables2/bootstrap.html'
        exclude = (
            'tf_beschreibung', 'enthalten_in_af', 'modell', 'tf_kritikalitaet', \
			'tf_eigentuemer_org', 'plattform', 'gf', 'af_gueltig_ab', 'af_gueltig_bis', 'direct_connect', \
			'hoechste_kritikalitaet_tf_in_af', 'gf_beschreibung', 'af_zuweisungsdatum', 'datum', \
			'geloescht', 'loeschdatum', \
			'userid_name__orga', \
			'userid_name__zi_organisation', \
        )

