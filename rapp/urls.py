"""books URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from . import admin

# app_name = 'rapp'		# Wird nur benötigt als namespace, falls mehrere Apps dieselbe Teil-URL haben

urlpatterns = [
	# path('', views.IndexView.as_view(), name='index'),
	path('', views.index, name='index'),
]



# Der Link auf die Gesamtliste
urlpatterns += [
	path('gesamtliste/', views.GesamtListView.as_view(), name='gesamtliste'),
]

# Der Link auf ein einzelnes Recht aus der Gesamtliste mit seiner generierten Detailsicht
urlpatterns += [
	path('gesamtliste/<int:pk>', views.GesamtDetailView.as_view(), name='gesamt-detail'),
]

# Der Link auf die User-liste
urlpatterns += [
	path('userliste/', views.UserIDundNameListView.as_view(), name='userliste'),
]


# Todo: Von den generischen Formularen für den User wird derzeit nur ...-update genutzt, der Rest geht über die Admin-Page --> Einbauen in Seiten überlegen

# Generische Formulare für CUD UserIDundName (werden im Frontend bedient)
urlpatterns += [
	path('user/<int:pk>/delete/', views.TblUserIDundNameDelete.as_view(), name='user-delete'),
	path('user/create/', views.TblUserIDundNameCreate.as_view(), name='user-create'),
	path('user/<int:pk>/update/', views.TblUserIDundNameUpdate.as_view(), name='user-update'),
	path('user/<int:pk>/toggle_geloescht/', views.userToggleGeloescht, name='user-toggle-geloescht'),
]

