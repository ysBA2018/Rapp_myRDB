from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Die Hilfsklasse zum Login: User John Doe einrichten und anmelden.
# Falls der User bereits existiert, einfach nur anmelden.
# Diese Klasse wird ausschließlich von den Testscripten verwendet

class Anmeldung():
	def login(self, loginfunc):
		user = authenticate(username='john', password='123')
		if user is None:
			# No backend authenticated the credentials
			user = User.objects.create_user(username='john', email='john@doe.com', password='123')
		loginfunc (username=user, password='123')

	def __init__(self, loginfunc):
		self.login (loginfunc)