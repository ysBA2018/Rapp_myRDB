"""RechteDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static


# Admin page URL for Project (not only app?)
urlpatterns = [
	url('admin/', admin.site.urls),
]


# Use include() to add paths from the rapp application
urlpatterns += [
	# url(r'rapp/', include('rapp.urls')),
	path('rapp/', include('rapp.urls')),
]

#Add URL maps to redirect the base URL to our application
urlpatterns += [
	path('', RedirectView.as_view(url='/rapp/')),
]

# use documentation feature
urlpatterns += [
	url('admin/doc/', include('django.contrib.admindocs.urls')),
]

#Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
	path('accounts/', include('django.contrib.auth.urls')),
]

# Use static() to add url mapping to serve static files during development (only)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

