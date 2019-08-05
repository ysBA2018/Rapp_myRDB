from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import TblUserhatrolle, hole_organisationen, User, TblUserIDundName
from .models import TblUserhatrolle, hole_organisationen
from urllib.parse import quote, unquote


# Das hätte man auch einfacher haben können, indem die relevanten Infos in views.py eingetragen worden wären
class ShowUhRForm(forms.ModelForm):
	class Meta:
		model = TblUserhatrolle
		fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]


# Hier ist das anders, weil eine Methode zur Klasse hinzugekommen ist:
# Initialisiere das Input Formular für neue Rolleneinträge mit der UserID, dem Modell und der Zuständigkeitsstufe
class CreateUhRForm(forms.ModelForm):
	class Meta:
		model = TblUserhatrolle
		fields = ['userid', 'rollenname', 'schwerpunkt_vertretung', 'bemerkung', ]

	def __init__(self, *args, **kwargs):
		"""
		Hole die 3 Parameter, die von der ReST-Schnittstelle übergeben wurden und fülle damit eine initial-Struktur.
		Damit werden die drei Werte Userid, Rollenname und Schweerpunkt/Vertretung initialisiert angezeigt.
		:param args:
		:param kwargs: Das Wesentliche steht hier drin
		"""

		self.userid = kwargs.pop('userid', None)
		if self.userid != None:
			self.userid = 'X' + self.userid[1:7].upper()
		self.rollenname = unquote(kwargs.pop('rollenname', 'Spielrolle'))
		self.schwerpunkt_vertretung = kwargs.pop('schwerpunkt_vertretung', 'Schwerpunkt')
		super(CreateUhRForm, self).__init__(*args, **kwargs)

		self.initial['userid'] = self.userid
		self.initial['rollenname'] = self.rollenname
		self.initial['schwerpunkt_vertretung'] = self.schwerpunkt_vertretung


#Auch hier ist das Thema das Initialisieren des Organisations-Choicefields
class ImportForm(forms.Form):
	# Die ersten Parameter, die für einen CSV-Import abgefragt werden müssen
	organisation = forms.ChoiceField(label='Organisation')
	datei = forms.FileField(label = 'Dateiname')

	def __init__(self, *args, **kwargs):
		super(ImportForm, self).__init__(*args, **kwargs)
		self.fields['organisation'].choices = hole_organisationen()

# Das hier behandelte boolean Field ist nicht Inhalt des Models, sondern ändert lediglich den Workflow
class ImportForm_schritt3(forms.Form):
	# Der Abschluss des zweiten Schritts besteht ebenfalls nur aus einer Bestätigung,
	# deshalb sind auch hier keine Datenfelder angegeben
	# (Eventuell kann hier noch ein Flag angegeben werden, ob Doppeleinträge gesucht wertden sollen)
	doppelte_suchen = forms.BooleanField(label = 'Suche nach doppelten Einträgen (optional)', required = False)

class CustomUserChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.get_full_name()

class CustomUserCreationForm(UserCreationForm):
	class Meta:
		model = User
		fields = ('username','email')

class CustomUserChangeForm(UserChangeForm):
	class Meta:
		model = User
		fields = ('username', 'email','userid_name')

class UserForm(forms.ModelForm):
	userid_name = CustomUserChoiceField(queryset=User.objects.all())
	class Meta:
		model = User
		fields = ('username', 'email','userid_name')

