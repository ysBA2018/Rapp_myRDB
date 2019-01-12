"""RechteDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from django.conf import settings
from django.conf.urls import include


admin.site.site_header = 'RechteDB - Adminseiten'
admin.site.site_title = 'RechteDB - Administration'
admin.site.index_title = 'RechteDB - Übersicht'

urlpatterns = [
	path('admin', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

from django.conf.urls import include
# Use include() to add paths from the rapp application
urlpatterns += [
	path('accounts/', include('django.contrib.auth.urls')),
	path('rapp/', include('rapp.urls')),
]

# Das ist die wichtigste Zeile: / wird auf /rapp gemappt
from django.views.generic import RedirectView
urlpatterns += [
	path('', RedirectView.as_view(url='/rapp')),
]
