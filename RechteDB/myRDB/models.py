import datetime
import json

from django.contrib.auth.base_user import BaseUserManager

from django.db import models

#from djongo import models as djongomodels
from django.utils import timezone

# Create your models here.



from django.apps import apps
import importlib

modellist = importlib.import_module('rapp.models')
TblRollen = modellist.TblRollen
TblRollehataf = modellist.TblRollehataf
TblUserhatrolle = modellist.TblUserhatrolle
TblUebersichtAfGfs = modellist.TblUebersichtAfGfs
TblOrga = modellist.TblOrga
TblUserIDundName = modellist.TblUserIDundName
TblPlattform = modellist.TblPlattform
TblGesamt = modellist.TblGesamt
TblGesamtHistorie = modellist.TblGesamtHistorie
TblAfliste = modellist.TblAfliste
Tblsachgebiete = modellist.Tblsachgebiete
Tblsubsysteme = modellist.Tblsubsysteme
TblDb2 = modellist.TblDb2
TblRacfGruppen = modellist.TblRacfGruppen
Tblrechteneuvonimport = modellist.Tblrechteneuvonimport
Tblrechteamneu = modellist.Tblrechteamneu
Qryf3Rechteneuvonimportduplikatfrei = modellist.Qryf3Rechteneuvonimportduplikatfrei
RACF_Rechte = modellist.RACF_Rechte
Orga_details = modellist.Orga_details
Letzter_import = modellist.Letzter_import
Modellierung = modellist.Modellierung
Direktverbindungen = modellist.Direktverbindungen
User = modellist.User
'''
class ChangeRequests(models.Model):
    requesting_user = models.CharField(max_length=7)
    compare_user = models.CharField(max_length=7)
    action = models.CharField(max_length=10)
    right_name = models.CharField(max_length=150)
    right_type = models.CharField(max_length=5)
    reason_for_action = models.CharField(max_length=500)
    status = models.CharField(max_length=10, default="unanswered")
    reason_for_decline = models.CharField(max_length=500, default="")
    created = models.DateTimeField(auto_now_add=True, editable=False,null=False, blank=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False,null=False, blank=False)


# Create your models here.
class Orga(models.Model):
    team = models.CharField(max_length=100)
    theme_owner = models.CharField(max_length=100)

    def __str__(self):
        return self.team


class Department(models.Model):
    department_name = models.CharField(max_length=8)

    def __str__(self):
        return self.department_name


class Group(models.Model):
    group_name = models.CharField(max_length=11)

    def __str__(self):
        return self.group_name


class ZI_Organisation(models.Model):
    zi_organisation_name = models.CharField(max_length=5)

    def __str__(self):
        return self.zi_organisation_name


class TF_Application(models.Model):
    application_name = models.CharField(max_length=100)
    color = models.CharField(default="hsl(0, 100, 100)",max_length=25)

    def __str__(self):
        return self.application_name


CHOICES = [(1, ' '), (2, 'K'), (3, 'U')]


class TF(models.Model):
    tf_name = models.CharField(max_length=100)
    tf_description = models.CharField(max_length=300)
    tf_owner_orga = djongomodels.EmbeddedModelField(model_container=Orga)
    tf_application = djongomodels.EmbeddedModelField(model_container=TF_Application)
    criticality = models.CharField(choices=CHOICES, max_length=1)
    highest_criticality_in_AF = models.CharField(choices=CHOICES, max_length=1)

    objects = djongomodels.DjongoManager()

    def __str__(self):
        return self.tf_name


class User_TF(models.Model):
    tf_name = models.CharField(max_length=100)
    model_tf_pk = models.IntegerField()
    color = models.CharField(default="hsl(0, 100, 100)", max_length=25)
    transfer = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    requested = models.BooleanField(default=False)


    objects = djongomodels.DjongoManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.tf_name


class GF(models.Model):
    gf_name = models.CharField(max_length=150)
    gf_description = models.CharField(max_length=250)
    tfs = djongomodels.ArrayReferenceField(to=TF, on_delete=models.CASCADE)

    objects = djongomodels.DjongoManager()

    def __str__(self):
        return self.gf_name


class User_GF(models.Model):
    gf_name = models.CharField(max_length=150)
    model_gf_pk = models.IntegerField()
    tfs = djongomodels.ArrayModelField(model_container=User_TF)
    transfer = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    requested = models.BooleanField(default=False)


    objects = djongomodels.DjongoManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.gf_name


class AF(models.Model):
    af_name = models.CharField(max_length=150)
    af_description = models.CharField(max_length=250)
    gfs = djongomodels.ArrayReferenceField(to=GF, on_delete=models.CASCADE)

    objects = djongomodels.DjongoManager()

    def __str__(self):
        return self.af_name


class User_AF(models.Model):
    af_name = models.CharField(max_length=150)
    model_af_pk = models.IntegerField()
    gfs = djongomodels.ArrayModelField(model_container=User_GF)
    af_applied = models.DateTimeField()
    af_valid_from = models.DateTimeField()
    af_valid_till = models.DateTimeField()
    transfer = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    requested = models.BooleanField(default=False)

    objects = djongomodels.DjongoManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.af_name


class Role(models.Model):
    role_name = models.CharField(max_length=150)
    role_description = models.CharField(max_length=250)
    afs = djongomodels.ArrayReferenceField(to=AF, on_delete=models.CASCADE)

    objects = djongomodels.DjongoManager()

    def __str__(self):
        return self.role_name


'''


