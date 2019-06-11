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
from rest_framework import routers
from myRDB import views
from . import settings

router = routers.DefaultRouter()
router.register(r'rollen', views.TblRollenViewSet, 'rolle')
router.register(r'rollehatafs', views.TblRollehatafViewSet, 'rollehataf')
router.register(r'userhatrollen', views.TblUserhatrolleViewSet, 'userhatrolle')
router.register(r'afgfs', views.TblUebersichtAfGfsViewSet, 'afgf')
router.register(r'orgas', views.TblOrgaViewSet, 'orga')
router.register(r'useridundnamen', views.TblUserIDundNameViewSet, 'useridundname')
router.register(r'plattformen', views.TblPlattformViewSet, 'plattform')
router.register(r'gesamte', views.TblGesamtViewSet, 'gesamt')
router.register(r'gesamtehistorie', views.TblGesamtHistorieViewSet, 'gesamthistorie')
router.register(r'afs', views.TblAflisteViewSet, 'af')
router.register(r'sachgebiete', views.TblsachgebieteViewSet, 'sachgebiet')
router.register(r'subsysteme', views.TblsubsystemeViewSet, 'subsystem')
router.register(r'db2s', views.TblDb2ViewSet, 'db2')
router.register(r'racfgruppen', views.TblRacfGruppenViewSet, 'racfgruppe')
router.register(r'rechteneuvonimport', views.TblrechteneuvonimportViewSet, 'rechtneuvonimport')
router.register(r'rechteamneu', views.TblrechteamneuViewSet, 'rechtamneu')
router.register(r'qriesf3rechteneuvonimportduplikatfrei', views.Qryf3RechteneuvonimportduplikatfreiViewSet, 'qryf3rechteneuvonimportduplikatfrei')
router.register(r'RACF_Rechte', views.RACF_RechteViewSet, 'RACF_Recht')
router.register(r'Orga_details', views.Orga_detailsViewSet, 'Orga_detail')
router.register(r'Letzte_imports', views.Letzter_importViewSet, 'Letzter_import')
router.register(r'Modellierungen', views.ModellierungViewSet, 'Modellierung')
router.register(r'Direktverbindungen', views.DirektverbindungenViewSet, 'Direktverbindung')


admin.site.site_header = 'RechteDB - Adminseiten'
admin.site.site_title = 'RechteDB - Administration'
admin.site.index_title = 'RechteDB - Übersicht'

urlpatterns = [
    path('admin', admin.site.urls)
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

from django.conf.urls import include
# Use include() to add paths from the rapp application
urlpatterns += [
    path('rapp/', include('rapp.urls')),
]

# Das ist die wichtigste Zeile: / wird auf /rapp gemappt
from django.views.generic import RedirectView
urlpatterns += [
    path('', RedirectView.as_view(url='/rapp')),
]

urlpatterns += [
    url(r'^api/', include((router.urls,'api'), namespace='myRDBNS')),
    path('', include('django.contrib.auth.urls')),
    path('myRDB/', include('myRDB.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]