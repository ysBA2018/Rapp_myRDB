import csv
import json
import re

import requests
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import datetime

from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from requests import ConnectionError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from .forms import CustomUserCreationForm, SomeForm, ApplyRightForm, DeleteRightForm, AcceptChangeForm, \
#   DeclineChangeForm, CustomAuthenticationForm, ProfileHeaderForm
from .models import *
from .forms import SomeForm, ApplyRightForm, DeleteRightForm, AcceptChangeForm, \
    DeclineChangeForm, CustomAuthenticationForm, ProfileHeaderForm

# from .models import Role, AF, GF, TF, Orga, Group, Department, ZI_Organisation, TF_Application, User_AF, User_TF, \
#   User_GF, ChangeRequests
from rest_framework import viewsets, status
from .serializers import *
# from .serializers import UserSerializer, RoleSerializer, AFSerializer, GFSerializer, TFSerializer, OrgaSerializer, \
#   GroupSerializer, DepartmentSerializer, ZI_OrganisationSerializer, TF_ApplicationSerializer, UserListingSerializer, \
#  CompleteUserListingSerializer, UserModelRightsSerializer, ChangeRequestsSerializer
from django.views import generic

from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordResetDoneView

User = get_user_model()
# docker_container_ip = "http://148.100.245.159:8000"
# proxies = {'http':"http://172.17.0.3:8000"}
# docker_container_ip = "http://0.0.0.0:8000"
docker_container_ip = "http://127.0.0.1:8000"


class CSVtoMongoDB(generic.FormView):
    '''
        dataimport-view: reads IIQ-csv (currently hardcoded) line by line and populates Database
            1 line equals 1 user-right
            creates user-profiles to be available for activation by signing-up user
            if element deosnt exist -> create and add reference to user model
            else add reference to user model
    '''
    template_name = 'myRDB/csvToMongo.html'
    form_class = SomeForm
    success_url = '#'

    def form_valid(self, form):
        self.start_import_action()
        return super().form_valid(form)

    def start_import_action(self):
        firstline = True
        # TODO: dateiimportfield und pfad müssen noch verbunden werden!
        #
        with open("myRDB_app/static/myRDB/data/Aus IIQ - User und TF komplett Neu_20180817_abMe.csv",
                  encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            cur_val = 0
            for line in csvreader:
                line = [re.sub(r'\s+', '', e) for e in line]

                if firstline == True:
                    firstline = False
                    pass
                else:
                    print(line)
                    orga = None
                    try:
                        orga = Orga.objects.get(team=line[8])
                    except(KeyError, Orga.DoesNotExist):
                        orga = Orga(team=line[8])
                    orga.save()

                    tf_application = None
                    try:
                        tf_application = TF_Application.objects.get(application_name=line[9])
                    except(KeyError, TF_Application.DoesNotExist):
                        right_color = "hsl(%d, 50%%, 50%%)" % cur_val
                        tf_application = TF_Application(application_name=line[9], color=right_color)
                        cur_val = (cur_val + 20) % 355

                    tf_application.save()

                    tf = None
                    try:
                        tf = TF.objects.get(tf_name=line[3])
                    except(KeyError, TF.DoesNotExist):
                        tf = TF(tf_name=line[3], tf_description=line[4], highest_criticality_in_AF=line[7],
                                tf_owner_orga=orga, tf_application=tf_application, criticality=line[10])
                    tf.save()

                    gf = None
                    try:
                        gf = GF.objects.get(gf_name=line[11])
                    except(KeyError, GF.DoesNotExist):
                        gf = GF(gf_name=line[11], gf_description=line[12])
                        gf.save()
                    gf.tfs.add(tf)
                    gf.save()

                    af = None
                    try:
                        af = AF.objects.get(af_name=line[5])
                    except(KeyError, AF.DoesNotExist):
                        af = AF(af_name=line[5], af_description=line[6])

                    af.save()
                    af.gfs.add(gf)

                    user = None
                    try:
                        user = User.objects.get(identity=line[0])
                        if user.name != line[1]:
                            user.name = line[1]
                        if user.first_name != line[2]:
                            user.first_name = line[2]
                        if user.username != line[0]:
                            user.username = line[0]
                    except(KeyError, User.DoesNotExist):
                        user = User(identity=line[0], name=line[1], first_name=line[2], username=line[0])
                        if not user.orga:
                            user.orga = Orga()
                        if not user.group:
                            user.group = Group()
                        if not user.department:
                            user.department = Department()
                        if not user.zi_organisation:
                            user.zi_organisation = ZI_Organisation()
                        if not user.roles:
                            user.roles = [Role()]
                        if not user.direct_connect_afs:
                            user.direct_connect_afs = [AF()]
                        if not user.direct_connect_gfs:
                            user.direct_connect_gfs = [GF()]
                        if not user.direct_connect_tfs:
                            user.direct_connect_tfs = [TF()]
                        if not user.my_requests:
                            user.my_requests = [ChangeRequests()]
                        if not user.user_afs:
                            user.user_afs = []
                        if not user.transfer_list:
                            user.transfer_list = []
                        if not user.delete_list:
                            user.delete_list = []
                    if user.user_afs.__len__() == 0:
                        user_tf = User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk, color=tf_application.color)
                        user_gf = User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk, tfs=[])
                        user_af = self.create_user_af(line, af)
                        user_gf.tfs.append(user_tf)
                        user_af.gfs.append(user_gf)
                        user.user_afs.append(user_af)
                    else:
                        afcount = 0
                        for uaf in user.user_afs:
                            if uaf.af_name != af.af_name:
                                afcount += 1
                            else:
                                gfcount = 0
                                for ugf in uaf.gfs:
                                    if ugf.gf_name != gf.gf_name:
                                        gfcount += 1
                                    else:
                                        tfcount = 0
                                        for utf in ugf.tfs:
                                            if utf.tf_name != tf.tf_name:
                                                tfcount += 1
                                            else:
                                                break
                                        if tfcount == ugf.tfs.__len__():
                                            ugf.tfs.append(User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk,
                                                                   color=tf_application.color))
                                if gfcount == uaf.gfs.__len__():
                                    uaf.gfs.append(User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk,
                                                           tfs=[User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk,
                                                                        color=tf_application.color)]))
                        if afcount == user.user_afs.__len__():
                            user_af = self.create_user_af(line, af)
                            user_af.gfs.append(User_GF(gf_name=gf.gf_name, model_gf_pk=gf.pk,
                                                       tfs=[User_TF(tf_name=tf.tf_name, model_tf_pk=tf.pk,
                                                                    color=tf_application.color)]))
                            user.user_afs.append(user_af)

                    user.direct_connect_afs.add(af)
                    user.save()

    def create_user_af(self, line, af):
        if line[15] == "" and line[16] == "" and line[17] == "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[])
        if line[15] != "" and line[16] == "" and line[17] == "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat())
        if line[15] != "" and line[16] != "" and line[17] == "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat()
                              , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat())
        if line[15] != "" and line[16] != "" and line[17] != "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_valid_from=datetime.datetime.strptime(line[15], "%d.%m.%Y").isoformat()
                              , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat()
                              , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
        if line[15] == "" and line[16] != "" and line[17] != "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_valid_till=datetime.datetime.strptime(line[16], "%d.%m.%Y").isoformat()
                              , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
        if line[15] == "" and line[16] == "" and line[17] != "":
            user_af = User_AF(af_name=af.af_name, model_af_pk=af.pk, gfs=[]
                              , af_applied=datetime.datetime.strptime(line[17], "%d.%m.%Y").isoformat())
        return user_af


class Login(LoginView):
    '''
        standard Loginview uses  django.auth includes CustomAuthentication-form
    '''
    template_name = 'myRDB/registration/login.html'
    authentication_form = CustomAuthenticationForm


class Logout(LogoutView):
    '''
        standard Logoutview uses django.auth includes CustomAuthentication-form
    '''
    template_name = 'myRDB/registration/logout.html'


class Register(generic.CreateView):
    '''
        standard Register view uses  django.auth includes CustomUserCreationForm-form
        currently without email-verification
    '''
    form_class = None
    # form_class = CustomUserCreationForm
    success_url = '/myRDB/login'
    template_name = 'myRDB/registration/register.html'


class Password_Reset(PasswordResetView):
    '''
        TODO: pw-reset not implemented yet due to not yet implemented email-verification
    '''
    template_name = 'myRDB/registration/password_reset_form.html'


class Password_Reset_Done(PasswordResetDoneView):
    '''
       TODO: pw-reset not implemented yet due to not yet implemented email-verification
    '''
    template_name = 'myRDB/registration/password_reset_done.html'


class Password_Reset_Confirm(PasswordResetConfirmView):
    '''
       TODO: pw-reset not implemented yet due to not yet implemented email-verification
    '''
    template_name = 'myRDB/registration/password_reset_confirm.html'


class Password_Reset_Complete(PasswordResetCompleteView):
    '''
       TODO: pw-reset not implemented yet due to not yet implemented email-verification
    '''
    template_name = 'myRDB/registration/password_reset_complete.html'


class IndexView(generic.ListView):
    '''
       Welcome-Page after login:
        loads user-data of logged-in user to welcome after login
    '''
    template_name = 'myRDB/index.html'
    queryset = User.objects.all()

    def get_queryset(self):
        logged_in_user = self.request.user
        return Response({'user': logged_in_user})


class Search_All(generic.ListView):
    '''
        Search-Function of the old RDB-APP:
            rebuilt to work with mongodb
            fills selectboxes for filters with data
            builds url by selected filters and requests data from REST-API
            prepares data for display in Table (before filter: all rights of all users, sorted by user)
    '''
    template_name = 'myRDB/search_all.html'
    extra_context = {}

    def get_queryset(self):
        # url = 'http://' + self.request.get_host() + '/searchlistings/'
        url = docker_container_ip + '/searchlistings/'
        headers = get_headers(self.request)
        lis = ['zi_organisations', 'orgas', 'tf_applications', 'departments', 'roles', 'groups']
        for e in lis:
            self.extra_context[e] = populate_choice_fields(headers, e, self.request)
        params, changed = build_url_params(self.request, self.extra_context)
        if 'entries_per_page' in self.request.GET:
            self.paginate_by = self.request.GET['entries_per_page']
            if self.paginate_by == '':
                self.paginate_by = 20
        else:
            self.paginate_by = 20
        if params == "":
            prefix = "?"
        else:
            prefix = "&"
        params = params + prefix + "entries_per_page=" + self.paginate_by.__str__()
        url = url + params

        if not self.extra_context.keys().__contains__('data') or changed == True:
            user_json_data = get_by_url(url, headers)
            self.extra_context['data'] = self.prepare_table_data(user_json_data, headers)
        self.extra_context['params_for_pagination'] = params
        return self.extra_context['data']

        # table=json2html.convert(json=user_json_data['results'])
        # print(table)
        # return Response(data=user_json_data, content_type='application/html')

    def prepare_table_data(self, json_data, headers):
        lines = []

        tf_json_data = get_tfs(get_headers(self.request), self.request)
        for user in json_data:
            for af in user['user_afs']:
                if self.request.GET.keys().__contains__('af_name'):
                    if not af['af_name'].__contains__(self.request.GET['af_name']):
                        continue
                for gf in af['gfs']:
                    if self.request.GET.keys().__contains__('gf_name'):
                        if not gf['gf_name'].__contains__(self.request.GET['gf_name']):
                            continue
                    for tf in gf['tfs']:
                        if self.request.GET.keys().__contains__('tf_name'):
                            if not tf['tf_name'].__contains__(self.request.GET['tf_name']):
                                continue
                        model_tf = [x for x in tf_json_data if x['pk'] == tf['model_tf_pk']].pop(0)
                        line = [user['identity'], user['name'], user['first_name'], tf['tf_name'], gf['gf_name'],
                                af['af_name'],
                                model_tf['tf_owner_orga']['team'],
                                model_tf['tf_application']['application_name'], model_tf['tf_description'], '',
                                user['deleted']]
                        lines.append(line)
                        '''
                        if self.extra_context.keys().__contains__(
                                'tf_owner_orga') and self.extra_context.keys().__contains__('tf_application'):
                            if model_tf['tf_owner_orga']['team'] == self.request.GET['tf_owner_orga'] and \
                                    model_tf['tf_application']['application_name'] == self.request.GET[
                                'tf_application']:
                                lines.append(line)
                        elif self.extra_context.keys().__contains__(
                                'tf_owner_orga') and not self.extra_context.keys().__contains__('tf_application'):
                            if model_tf['tf_owner_orga']['team'] == self.request.GET['tf_owner_orga']:
                                lines.append(line)
                        elif not self.extra_context.keys().__contains__(
                                'tf_owner_orga') and self.extra_context.keys().__contains__('tf_application'):
                            if model_tf['tf_application']['application_name'] == self.request.GET['tf_application']:
                                lines.append(line)
                        else:
                            lines.append(line)
                            '''
        return lines


class Users(generic.ListView):
    '''
        Userlisting:
            requests all users from REST-API and displays them as paginated list
            selectbox filters get populated
            links to userprofiles of each user in list
    '''
    template_name = 'myRDB/users.html'
    extra_context = {}

    def get_queryset(self):
        logged_in_user_token = self.request.user.auth_token
        # url = 'http://' + self.request.get_host() + '/userlistings/'
        url = docker_container_ip + '/userlistings/'
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        lis = ['zi_organisations', 'orgas', 'departments', 'roles', 'groups']
        for e in lis:
            self.extra_context[e] = populate_choice_fields(headers, e, self.request)
        params, changed = build_url_params(self.request, self.extra_context)
        if 'entries_per_page' in self.request.GET:
            self.paginate_by = self.request.GET['entries_per_page']
            if self.paginate_by == '':
                self.paginate_by = 10
        else:
            self.paginate_by = 10
        if params == "":
            prefix = "?"
        else:
            prefix = "&"
        params = params + prefix + "entries_per_page=" + self.paginate_by.__str__()
        url = url + params
        self.extra_context['params_for_pagination'] = params

        if changed == True or not self.extra_context.keys().__contains__('paginated_users'):
            user_json_data = get_by_url(url, headers=headers)
            # user_count= user_json_data['count']
            users = {'users': user_json_data}
            self.extra_context['paginated_users'] = users
        else:
            users = self.extra_context['paginated_users']
        response = Response(users)
        print(response.data['users'])

        user_paginator = Paginator(response.data['users'], self.paginate_by)
        page = self.request.GET.get('page')
        try:
            user_paged_data = user_paginator.page(page)
        except PageNotAnInteger:
            user_paged_data = user_paginator.page(1)
        except EmptyPage:
            user_paged_data = user_paginator.page(user_paginator.num_pages)

        self.extra_context['paged_data'] = user_paged_data
        return response.data['users']


def populate_choice_fields(headers, field, request):
    '''
        method to populate selectboxes with data from REST-API
        used by search and users
    '''
    # url = 'http://' + request.get_host() + '/' + field + '/'
    url = docker_container_ip + '/' + field + '/'
    json_data = get_by_url(url, get_headers(request))
    if type(json_data) == list:
        results = {field: json_data}
    if type(json_data) == dict:
        results = {field: json_data['results']}
    response = Response(results)
    return response.data[field]


def build_url_params(request, extra_context):
    '''
        method for url-buildup for REST-API -requests
        used by search and users
    '''
    params = ""
    changed = False
    if 'userSearch' in request.GET:
        user_search = request.GET['userSearch']
        search_what = request.GET['search_what']
        if extra_context.keys().__contains__("user_search"):
            if user_search != extra_context["user_search"] or search_what != extra_context["search_what"]:
                changed = True
        else:
            changed = True
        extra_context["userSearch"] = user_search
        extra_context["search_what"] = search_what
        params = "?userSearch=" + user_search + "&search_what=" + search_what
    if 'zi_organisation' in request.GET:
        zi_organisation = '----'
        if not request.GET['zi_organisation'] == '----':
            zi_organisation = request.GET['zi_organisation']
            params = params + "&zi_organisation=" + zi_organisation
        if extra_context.keys().__contains__("zi_organisation"):
            if zi_organisation != extra_context["zi_organisation"]:
                changed = True
        else:
            changed = True
        extra_context["zi_organisation"] = zi_organisation
    if 'department' in request.GET:
        department = '----'
        if not request.GET['department'] == '----':
            department = request.GET['department']
            params = params + "&department=" + department
        if extra_context.keys().__contains__("department"):
            if department != extra_context["department"]:
                changed = True
        else:
            changed = True
        extra_context["department"] = department
    if 'orga' in request.GET:
        orga = '----'
        if not request.GET['orga'] == '----':
            orga = request.GET['orga']
            params = params + "&orga=" + orga
        if extra_context.keys().__contains__("orga"):
            if orga != extra_context["orga"]:
                changed = True
        else:
            changed = True
        extra_context["orga"] = orga
    if 'tf_owner_orga' in request.GET:
        tf_owner_orga = '----'
        if not request.GET['tf_owner_orga'] == '----':
            tf_owner_orga = request.GET['tf_owner_orga']
            params = params + "&tf_owner_orga=" + tf_owner_orga
        if extra_context.keys().__contains__("tf_owner_orga"):
            if tf_owner_orga != extra_context["tf_owner_orga"]:
                changed = True
        else:
            changed = True
        extra_context["tf_owner_orga"] = tf_owner_orga
    if 'tf_application' in request.GET:
        tf_application = '----'
        if not request.GET['tf_application'] == '----':
            tf_application = request.GET['tf_application']
            params = params + "&tf_application=" + tf_application
        if extra_context.keys().__contains__("tf_application"):
            if tf_application != extra_context["tf_application"]:
                changed = True
        else:
            changed = True
        extra_context["tf_application"] = tf_application
    if 'role' in request.GET:
        role = '----'
        if not request.GET['role'] == '----':
            role = request.GET['role']
            params = params + "&role=" + role
        if extra_context.keys().__contains__("role"):
            if role != extra_context["role"]:
                changed = True
        else:
            changed = True
        extra_context["role"] = role
    if 'group' in request.GET:
        group = '----'
        if not request.GET['group'] == '----':
            group = request.GET['group']
            params = params + "&group=" + group
        if extra_context.keys().__contains__("group"):
            if group != extra_context["group"]:
                changed = True
        else:
            changed = True
        extra_context["group"] = group
    if 'af_name' in request.GET:
        af_name = ''
        if not request.GET['af_name'] == '':
            af_name = request.GET['af_name']
            params = params + "&af_name=" + af_name
        if extra_context.keys().__contains__("af_name"):
            if af_name != extra_context["af_name"]:
                changed = True
        else:
            changed = True
        extra_context["af_name"] = af_name
    if 'gf_name' in request.GET:
        gf_name = ''
        if not request.GET['gf_name'] == '':
            gf_name = request.GET['gf_name']
            params = params + "&gf_name=" + gf_name
        if extra_context.keys().__contains__("gf_name"):
            if gf_name != extra_context["gf_name"]:
                changed = True
        else:
            changed = True
        extra_context["gf_name"] = gf_name
    if 'tf_name' in request.GET:
        tf_name = ''
        if not request.GET['tf_name'] == '':
            tf_name = request.GET['tf_name']
            params = params + "&tf_name=" + tf_name
        if extra_context.keys().__contains__("tf_name"):
            if tf_name != extra_context["tf_name"]:
                changed = True
        else:
            changed = True
        extra_context["tf_name"] = tf_name

    return params, changed


class Compare(generic.ListView):
    '''
        compare-view:
            compares userdata with data of a selected user
            reachable by form from each user-profile
            requests user- and compareuser-data from REST-API andprepares data for presentation as
                circlepacking or table, scatterplot
                sets context-variables for use in templates and session variables

    '''
    model = User
    template_name = 'myRDB/compare/compare.html'
    # paginate_by = 10
    context_object_name = "table_data"
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            if 'user_search' in self.request.GET.keys():
                compareUserIdentity = self.request.GET['user_search']
            else:
                compareUserIdentity = self.request.session.get('user_search')

            self.request.session['user_search'] = compareUserIdentity

            headers = get_headers(self.request)

            user = get_user_by_name(compareUserIdentity, headers, self.request)[0]

            user_json_data = get_user_by_key(user['id'], headers=headers, request=self.request)

            graph_data, scatterData, counts = prepareJSONdata(user, user_json_data, True, headers, self.request)

            #compUserRoles = user_json_data['roles']
            #compUserAfs = user_json_data['children']

            #data, comp_gf_count, comp_tf_count = prepareTableData(user_json_data, compUserRoles, compUserAfs, headers)

            context['comp_user_count'] = counts['user']
            context['comp_role_count'] = counts['roles']
            context['comp_af_count'] = counts['afs']
            context['comp_gf_count'] = counts['gfs']
            context['comp_tf_count'] = counts['tfs']
            print(user_json_data)
            context["compareUser"] = user_json_data
            if graph_data['children']:
                context['compare_user_department'] = graph_data['children'][0]['gruppe']
            else:
                context['compare_user_department'] = "Kein Nutzer & daher keine Gruppe zugewiesen!"
            #context["compareUser_table_data"] = data
            context["compareUser_graph_data"] = graph_data

            return context
        except IOError:
            print("Error at compareUser")
        return context

    def get_queryset(self):
        try:
            self.extra_context['current_site'] = "compare"
            setViewMode(self.request, self.extra_context)
            headers = get_headers(self.request)

            if not "user_identity" in self.request.GET.keys():
                user = self.request.user
                self.extra_context['identity_param'] = self.request.session.get('user_identity')
            else:
                # TODO: hier noch lösung mit Params über API finden!
                self.extra_context['identity_param'] = self.request.GET['user_identity']
                user = get_user_by_name(self.extra_context['identity_param'], headers, self.request)[0]


            self.request.session['user_identity'] = self.extra_context['identity_param']
            logged_in_user_token = self.request.user.auth_token
            user_json_data = get_user_by_key(user['id'], headers, self.request)

            #roles = user_json_data['roles']
            try:
                graph_data, scatterData, counts = prepareJSONdata(user['id'], user_json_data, False, headers, self.request)
                self.extra_context['jsondata'] = graph_data
                # afs = user_json_data['children']

                # data, gf_count, tf_count = prepareTableData(user_json_data, roles, afs, headers)
                self.extra_context['user_identity'] = user_json_data['username']
                self.extra_context['user_first_name'] = user_json_data['first_name']
                self.extra_context['user_name'] = user_json_data['last_name']
                if graph_data['children']:
                    self.extra_context['user_department'] = graph_data['children'][0]['gruppe']
                else:
                    self.extra_context['user_department'] = "Kein Nutzer & daher keine Gruppe zugewiesen!"
                self.extra_context['user_count'] = counts['user']
                self.extra_context['role_count'] = counts['roles']
                self.extra_context['af_count'] = counts['afs']
                self.extra_context['gf_count'] = counts['gfs']
                self.extra_context['tf_count'] = counts['tfs']
            except IOError:
                print("Error at compar - creating user_graph")
            try:
                transfer_graph_data, transfer_list_with_category, transfer_rights_count = prepareTransferJSONdata(
                user_json_data, self.request, headers)
                self.extra_context['transfer_list_count'] = transfer_rights_count

                self.extra_context['transferlist'] = transfer_graph_data
                # transfer_list_table_data, transfer_list_count = prepareTransferTabledata(transfer_list)
                # self.extra_context['transfer_list_table_data'] = transfer_list_table_data
            except IOError:
                print("Error at compar - creating transfer_graph")


            #delete_list = user_json_data['delete_list']
            try:
                delete_graph_data, delete_list_with_category, delete_rights_count = prepareDeleteJSONdata(user_json_data,
                                                                                                          self.request, headers)
                #delete_list_table_data, delete_list_count = prepareTrashTableData(delete_list)
                #self.extra_context['delete_list_table_data'] = delete_list_table_data
                self.extra_context['delete_list_count'] = delete_rights_count
                self.extra_context['deletelist'] = delete_graph_data
            except IOError:
                print("Error at compar - creating delete_graph")

            return []#data
        except IOError:
            print("Error at Compare - comparingUser")
        return []  # data


class ProfileRightsAnalysis(generic.ListView):
    '''
        rights-analysis-view:
            uses session data from userprofile
            presorts userrights for display in equal and unequal in comparison to original-right-model
            prepares data for display as circlepacking structures
            counts matching and nonmatching rights in a rightspackage
            switchable between AF- and GF- analysis
            includes linkage to right-application-view for applying transfered or deleted rights
    '''
    model = User
    template_name = 'myRDB/profileRightsAnalysis/profile_rights_analysis.html'
    extra_context = {}

    def get_queryset(self):
        self.extra_context['current_site'] = "analysis"
        setViewMode(self.request, self.extra_context)

        user_data = self.request.session.get('user_data')
        table_data = self.request.session.get('table_data')
        delete_graph_data = self.request.session.get('delete_list_graph_data')
        transfer_graph_data = self.request.session.get('transfer_list_graph_data')
        delete_table_data = self.request.session.get('delete_list_table_data')
        transfer_table_data = self.request.session.get('transfer_list_table_data')
        transfer_list_count = self.request.session.get('transfer_list_count')
        delete_list_count = self.request.session.get('delete_list_count')
        self.extra_context['delete_list_table_data'] = delete_table_data
        self.extra_context['transfer_list_table_data'] = transfer_table_data
        self.extra_context['deletelist'] = delete_graph_data
        self.extra_context['transferlist'] = transfer_graph_data
        self.extra_context['transfer_list_count'] = transfer_list_count
        self.extra_context['delete_list_count'] = delete_list_count

        if self.request.GET.keys().__contains__("level"):
            self.extra_context['level'] = self.request.GET['level']
        else:
            self.extra_context['level'] = 'AF'
        logged_in_user_token = self.request.user.auth_token
        headers = {'Authorization': 'Token ' + logged_in_user_token.key}
        equalRights = []
        unequalRights = []
        equalModelRights = []
        unequalModelRights = []
        equalRightsStats = []
        unequalRightsStats = []

        equalModelRights, equalRights, equalRightsStats, unequalModelRights, unequalRights, unequalRightsStats = self.compare_right_and_modelright(
            equalModelRights, equalRights, equalRightsStats, headers, unequalModelRights, unequalRights,
            unequalRightsStats, user_data)

        self.extra_context['equal_rights'] = sorted(equalRights, key=lambda k: k['name'])
        self.extra_context['unequal_rights'] = sorted(unequalRights, key=lambda k: k['name'])
        self.extra_context['equal_model_rights'] = sorted(equalModelRights, key=lambda k: k['name'])
        self.extra_context['unequal_model_rights'] = sorted(unequalModelRights, key=lambda k: k['name'])
        self.extra_context['equal_rights_stats'] = sorted(equalRightsStats, key=lambda k: k['right_name'])
        self.extra_context['unequal_rights_stats'] = sorted(unequalRightsStats, key=lambda k: k['right_name'])

        self.extra_context['user_identity'] = user_data['identity']
        self.extra_context['user_first_name'] = user_data['first_name']
        self.extra_context['user_name'] = user_data['name']
        self.extra_context['user_department'] = user_data['department']
        self.extra_context['role_count'] = self.request.session.get('role_count')
        self.extra_context['af_count'] = self.request.session.get('af_count')
        self.extra_context['gf_count'] = self.request.session.get('gf_count')
        self.extra_context['tf_count'] = self.request.session.get('tf_count')
        return None

    def compare_right_and_modelright(self, equalModelRights, equalRights, equalRightsStats, headers, unequalModelRights,
                                     unequalRights, unequalRightsStats, user_data):
        if self.extra_context['level'] == "AF":
            afs = sorted(user_data['children'], key=lambda k: k['name'])
            for af in afs:
                through = False
                model_afs = iter(
                    sorted(get_user_model_rights_by_key(user_data['pk'], headers, self.request)['direct_connect_afs'],
                           key=lambda k: k['af_name']))
                # if af['name'] != "":  # wegen direct_connect_gfs <-> af.af_name = "" <-> muss noch beim einlesen der daten umgebaut werden
                while not through:
                    try:
                        current_model = next(model_afs)
                    except StopIteration:
                        print('model_af stop iteration')
                        through = True
                    if af['name'] == current_model['af_name']:
                        stats = {}
                        stats['right_name'] = current_model['af_name']
                        stats['description'] = current_model['af_description']
                        self.prepareModelJSONdata(current_model, True, False, headers)
                        equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats = self.compareRightToModel(
                            af,
                            current_model,
                            equalRights,
                            unequalRights,
                            equalModelRights,
                            unequalModelRights,
                            True,
                            False,
                            stats,
                            unequalRightsStats,
                            equalRightsStats)
                        through = True;
                        break

                # else:
                #    afs.remove(af)
        elif self.extra_context['level'] == "GF":
            afs = user_data['children']
            gfs = []
            for af in afs:
                for gf in af['children']:
                    gfs.append(gf)
            gfs = sorted(gfs, key=lambda k: k['name'])

            model_afs = get_user_model_rights_by_key(user_data['pk'], headers, self.request)['direct_connect_afs']
            model_gfs = []
            for af in model_afs:
                for gf in af['gfs']:
                    model_gfs.append(gf)
            model_gfs = iter(sorted(model_gfs, key=lambda k: k['gf_name']))

            for gf in gfs:
                through = False
                # if gf['name'] != "":  # wegen direct_connect_gfs <-> af.af_name = "" <-> muss noch beim einlesen der daten umgebaut werden
                while not through:
                    try:
                        current_model = next(model_gfs)
                    except StopIteration:
                        print("in GF-StopIteration!")
                        through = True
                    if gf['name'] == current_model['gf_name']:
                        stats = {}
                        stats['right_name'] = current_model['gf_name']
                        stats['description'] = current_model['gf_description']
                        self.prepareModelJSONdata(current_model, False, True, headers)
                        equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats = self.compareRightToModel(
                            gf,
                            current_model,
                            equalRights,
                            unequalRights,
                            equalModelRights,
                            unequalModelRights,
                            False,
                            True,
                            stats,
                            unequalRightsStats,
                            equalRightsStats)
                        through = True
                        break

                # else:
                #    gfs.remove(gf)
        return equalModelRights, equalRights, equalRightsStats, unequalModelRights, unequalRights, unequalRightsStats

    def compareRightToModel(self, userRight, compareModel, equalRights, unequalRights, equalModelRights,
                            unequalModelRights, isAF, isGF, stats, unequalRightsStats, equalRightsStats):
        equal = False
        equalGFSum = 0
        equalTFSum = 0

        tf_count = 0
        model_tf_count = 0
        tf_count_diff = 0

        if isAF:
            modelGFIter = iter(sorted(compareModel['children'], key=lambda k: k['name']))

            gf_count = len(userRight['children'])
            model_gf_count = len(compareModel['children'])
            gf_count_diff = model_gf_count - gf_count

            stats['gf_count'] = gf_count
            stats['model_gf_count'] = model_gf_count
            stats['gf_count_diff'] = gf_count_diff

            for gf in sorted(userRight['children'], key=lambda k: k['name']):
                try:
                    currentGFModel = next(modelGFIter)
                except StopIteration:
                    print("in StopIteration")
                    break

                if gf['name'] == currentGFModel['name']:
                    equalGFSum += 1
                modelTFIter = iter(sorted(currentGFModel['children'], key=lambda k: k['name']))

                model_tf_count += len(currentGFModel['children'])
                tf_count += len(gf['children'])
                tf_count_diff = model_tf_count - tf_count

                for tf in sorted(gf['children'], key=lambda k: k['name']):
                    currentTFModel = next(modelTFIter)
                    if tf['name'] == currentTFModel['name']:
                        equalTFSum += 1
            if equalGFSum == gf_count and equalTFSum == tf_count and gf_count_diff == 0 and tf_count_diff == 0:
                equal = True
        if isGF:
            modelTFIter = iter(sorted(compareModel['children'], key=lambda k: k['name']))

            model_tf_count += len(compareModel['children'])
            tf_count += len(userRight['children'])
            tf_count_diff = model_tf_count - tf_count

            for tf in sorted(userRight['children'], key=lambda k: k['name']):
                currentTFModel = next(modelTFIter)
                if tf['name'] == currentTFModel['name']:
                    equalTFSum += 1
            if equalTFSum == tf_count and tf_count_diff == 0:
                equal = True

        stats['tf_count'] = tf_count
        stats['model_tf_count'] = model_tf_count
        stats['tf_count_diff'] = tf_count_diff

        if equal:
            equalModelRights.append(compareModel)
            equalRights.append(userRight)
            equalRightsStats.append(stats)
        else:
            unequalModelRights.append(compareModel)
            unequalRights.append(userRight)
            unequalRightsStats.append(stats)
        return equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats

    def prepareModelJSONdata(self, json_data, is_af, is_gf, headers):
        if is_af:
            json_data["name"] = json_data.pop('af_name')
            json_data["children"] = json_data.pop('gfs')
            for gf in json_data['children']:
                gf["name"] = gf.pop('gf_name')
                gf["children"] = gf.pop('tfs')
                for tf in gf['children']:
                    tf["name"] = tf.pop('tf_name')
                    tf["size"] = 2000
        if is_gf:
            json_data["name"] = json_data.pop('gf_name')
            json_data["children"] = json_data.pop('tfs')
            for tf in json_data['children']:
                tf["name"] = tf.pop('tf_name')
                tf["size"] = 2000


class Profile(generic.ListView):
    '''
        profile-view:
            gets specific user data from REST-API
            prepares it for display as circlepacking or table, scatterplot
            loads legend-data
            sets contextvariables for use in templates, sets sessionvariables for use in other views
    '''
    # model = User
    template_name = 'myRDB/profile/profile.html'
    # paginate_by = 10
    context_object_name = "table_data"
    extra_context = {}

    def get_queryset(self):
        self.extra_context['current_site'] = "profile"
        self.extra_context['current_host'] = docker_container_ip
        self.extra_context['profile_header_form'] = ProfileHeaderForm
        setViewMode(self.request, self.extra_context)
        print(self.request.get_host())
        if not "identity" in self.request.GET.keys():
            user = self.request.user
            self.request.session['user_identity'] = user.username
            user_id = user.username
            self.extra_context['identity_param'] = user.username
        else:
            # TODO: hier noch lösung mit Params über API finden!
            self.extra_context['identity_param'] = self.request.GET['identity']
            self.request.session['user_identity'] = self.extra_context['identity_param']
            user_id = self.request.GET['identity']

        headers = get_headers(self.request)

        legend_data = get_tf_applications(headers, self.request)

        sorted_legend_data = sorted(legend_data, key=lambda r: r["tf_technische_plattform"])
        self.extra_context['legendData'] = sorted_legend_data
        user_pk = user.pk
        user_json_data = get_user_by_key(user_pk, headers, self.request)

        last_import = get_last_import(headers)[0]['end']
        last_import_datetime = datetime.datetime.strptime(last_import,'%Y-%m-%dT%H:%M:%S.%fZ')
        last_rights_update = user.last_rights_update
        if last_rights_update is None or last_import_datetime > last_rights_update.replace(tzinfo=None):
            update_personal_right_models(user_json_data, headers, self.request)
            last_rights_update = datetime.datetime.now()
            patch_user_last_rights_update(user_pk,last_rights_update,headers)
        graph_data, scatterData, counts = prepareJSONdata(user_id, user_json_data, False, headers, self.request)
        self.extra_context['scatterData'] = scatterData

        transfer_graph_data, transfer_list_with_category, transfer_rights_count = prepareTransferJSONdata(user_json_data,
                                                                             self.request, headers)
        self.extra_context['transferlist'] = transfer_graph_data
        # transfer_list_table_data, transfer_list_count = prepareTransferTabledata(transfer_list)
        # self.extra_context['transfer_list_table_data'] = transfer_list_table_data
        self.extra_context['transfer_list_count'] = transfer_rights_count

        delete_graph_data, delete_list_with_category, delete_rights_count = prepareDeleteJSONdata(user_json_data,
                                                                                                  self.request, headers)
        # delete_list, delete_list_with_category = [],[]
        self.extra_context['deletelist'] = delete_graph_data
        # delete_list_table_data, delete_list_count = prepareTrashTableData(delete_list)
        # self.extra_context['delete_list_table_data'] = delete_list_table_data
        self.extra_context['delete_list_count'] = delete_rights_count

        # afs = user_json_data['children']
        # data, gf_count, tf_count = prepareTableData(user_json_data, roles, afs, headers)

        self.request.session['user_data'] = graph_data

        # self.request.session['table_data'] = data
        self.request.session['delete_list_graph_data'] = delete_graph_data
        # self.request.session['delete_list_table_data'] = delete_list_table_data
        self.request.session['delete_list_count'] = delete_rights_count
        self.request.session['transfer_list_graph_data'] = transfer_graph_data
        # self.request.session['transfer_list_table_data'] = transfer_list_table_data
        self.request.session['transfer_list_count'] = transfer_rights_count

        self.extra_context['user_count'] = counts['user']
        self.extra_context['role_count'] = counts['roles']
        self.extra_context['af_count'] = counts['afs']
        self.extra_context['gf_count'] = counts['gfs']
        self.extra_context['tf_count'] = counts['tfs']

        self.extra_context['jsondata'] = graph_data

        self.extra_context['user_id'] = user.pk
        self.extra_context['user_identity'] = user.username
        self.extra_context['user_first_name'] = user.first_name
        self.extra_context['user_name'] = user.last_name
        if graph_data['children']:
            self.extra_context['user_department'] = graph_data['children'][0]['gruppe']
        else:
            self.extra_context['user_department'] = "Kein Nutzer & daher keine Gruppe zugewiesen!"

        self.request.session['user_count'] = counts['user']
        self.request.session['role_count'] = counts['roles']
        self.request.session['af_count'] = counts['afs']
        self.request.session['gf_count'] = counts['gfs']
        self.request.session['tf_count'] = counts['tfs']

        return []
        # return data


class RequestPool(generic.ListView):
    '''
        changerequest-collection-view:
            displays all changerequests sorted, grouped by users
            prepares data and forms for display
            sets context-variable
    '''
    model = None
    # model = ChangeRequests
    template_name = 'myRDB/requestPool/request_pool.html'
    extra_context = {}
    context_object_name = 'list_data'

    def get_queryset(self):
        change_requests_json_data = get_changerequests(get_headers(self.request), self.request)
        print(change_requests_json_data)
        requests_by_users = self.repack_data(change_requests_json_data)
        print(requests_by_users)
        self.extra_context['requesting_users'] = requests_by_users
        self.extra_context['accept_form'] = AcceptChangeForm
        self.extra_context['decline_form'] = DeclineChangeForm
        return []

    def repack_data(self, change_requests):
        list_by_user = []
        for data in change_requests:
            if data['status'] == "unanswered":
                user_dict = {'requesting_user': data['requesting_user'], 'apply_requests': [], 'delete_requests': []}
                if not list_by_user.__contains__(user_dict):
                    list_by_user.append(user_dict)

        for data in change_requests:
            for user in list_by_user:
                if user['requesting_user'] == data['requesting_user']:
                    requesting_user = get_user_by_key(data['requesting_user'],
                                                      headers=get_headers(self.request), request=self.request)
                    if data['status'] == "unanswered":
                        # TODO: xv-nummer als SLUG-Field -> dann url über xvnummer aufrufbar
                        if data['action'] == 'apply':
                            right = get_right_from_list(requesting_user, data['right_type'], data['right_name'],
                                                        requesting_user['transfer_list'])
                            if right is None:
                                model = None
                            else:
                                model = get_model_right(requesting_user, data['right_type'], right['model_right_pk'],
                                                        self.request)
                            user["apply_requests"].append({'right': right, 'model': model, 'type': data['right_type'],
                                                           'right_name': data['right_name'],
                                                           'reason_for_action': data['reason_for_action'],
                                                           'request_pk': data['pk']})
                        else:
                            right = get_right_from_list(requesting_user, data['right_type'], data['right_name'],
                                                        requesting_user['delete_list'])
                            if right is None:
                                model = None
                            else:
                                model = get_model_right(requesting_user, data['right_type'], right['model_right_pk'],
                                                        self.request)
                            user["delete_requests"].append({'right': right, 'model': model, 'type': data['right_type'],
                                                            'right_name': data['right_name'],
                                                            'reason_for_action': data['reason_for_action'],
                                                            'request_pk': data['pk']})

        return list_by_user


class MyRequests(generic.ListView):
    '''
        user-changerequests:
            gets specific user-changerequest-fata over REST-API
            presorts requests in accepted,declined and unanswered
            prepares data for display as circlepackings
            sets contextvariables
    '''
    model = None
    # model = ChangeRequests
    template_name = 'myRDB/myRequests/my_requests.html'
    extra_context = {}
    context_object_name = "accepted_list"

    def post(self, request, *args, **kwargs):
        print("I'm in my_requests-post")
        return HttpResponseRedirect(self.request.path_info)

    def get_queryset(self):
        self.extra_context['current_site'] = "my_requests"
        if 'user_identity' in self.request.session:
            user_identity = self.request.session.get('user_identity')
        else:
            user_identity = self.request.user.identity
        self.extra_context['requesting_user'] = user_identity
        # setViewMode(self.request, self.extra_context)
        user = get_user_by_key(user_identity, get_headers(self.request), self.request)
        request_list = self.get_my_requests(user)
        repacked_request_list = self.repack_list(request_list)
        unanswered_list, accepted_list, declined_list = self.presort(repacked_request_list)
        self.extra_context['declined_list'] = declined_list
        self.extra_context['unanswered_list'] = unanswered_list
        return accepted_list

    def repack_list(self, list):
        repacked_list = []
        for request in list:
            requesting_user = get_user_by_key(request['requesting_user'], headers=get_headers(self.request),
                                              request=self.request)
            if request['action'] == 'apply':
                # TODO: wenn berechtigung auf comp_user oder user seite gelöscht wurde -> zuerst modell-recht anzeigen -> wenn auch gelöscht - dann erst None setzen und damit esatz-circle anzeigen
                if request['status'] == "accepted":
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['user_afs'])
                    if right is None:
                        model = None
                    else:
                        model = get_model_right(requesting_user, request['right_type'], right['model_right_pk'],
                                                self.request)
                elif request['status'] == "declined":
                    compare_user = get_user_by_key(request['compare_user'], headers=get_headers(self.request),
                                                   request=self.request)
                    right = get_right_from_list(compare_user, request['right_type'], request['right_name'],
                                                compare_user['user_afs'])
                    if right is None:
                        model = None
                    else:
                        model = get_model_right(compare_user, request['right_type'], right['model_right_pk'],
                                                self.request)
                else:
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['transfer_list'])
                    if right is None:
                        model = None
                    else:
                        model = get_model_right(requesting_user, request['right_type'], right['model_right_pk'],
                                                self.request)
            if request['action'] == 'delete':
                if request['status'] == "accepted":
                    right = None
                    model = None
                elif request['status'] == "declined":
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['user_afs'])
                    if right is None:
                        model = None
                    else:
                        model = get_model_right(requesting_user, request['right_type'], right['model_right_pk'],
                                                self.request)
                else:
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['delete_list'])
                    if right is None:
                        model = None
                    else:
                        model = get_model_right(requesting_user, request['right_type'], right['model_right_pk'],
                                                self.request)
            repacked_list.append({'right': right, 'model': model, 'request': request})
        return repacked_list

    def presort(self, list):
        unanswered_dict = {'apply': [], 'delete': []}
        accepted_dict = {'apply': [], 'delete': []}
        declined_dict = {'apply': [], 'delete': []}
        for request in list:
            if request['request']['status'] == 'unanswered':
                if request['request']['action'] == 'apply':
                    unanswered_dict['apply'].append(request)
                if request['request']['action'] == 'delete':
                    unanswered_dict['delete'].append(request)
            if request['request']['status'] == 'accepted':
                if request['request']['action'] == 'apply':
                    accepted_dict['apply'].append(request)
                if request['request']['action'] == 'delete':
                    accepted_dict['delete'].append(request)
            if request['request']['status'] == 'declined':
                if request['request']['action'] == 'apply':
                    declined_dict['apply'].append(request)
                if request['request']['action'] == 'delete':
                    declined_dict['delete'].append(request)
        return unanswered_dict, accepted_dict, declined_dict

    def get_my_requests(self, user):
        request_list = []
        for request in user['my_requests']:
            request_list.append(get_by_url(request, get_headers(self.request)))
        return request_list


class RightApplication(generic.ListView):
    '''
        rightapplication-view:
            gets user-data by REST-API
            prepares all data of transfer- and deletelist of user as circlepackings to display
            sets context variables

    '''
    model = User
    template_name = 'myRDB/rightApplication/right_application.html'
    extra_context = {}
    context_object_name = "list_data"

    def get_queryset(self):
        self.extra_context['current_site'] = "right_application"
        self.extra_context['compare_user'] = self.request.session.get('user_search')
        user_identity = self.request.session.get('user_identity')
        self.extra_context['requesting_user'] = user_identity
        # setViewMode(self.request, self.extra_context)
        headers = get_headers(self.request)
        user_json_data = get_user_by_key(user_identity, headers, self.request)

        roles = user_json_data['roles']

        user_json_data, scatterData = prepareJSONdata(user_json_data['identity'], user_json_data, False, headers,
                                                      self.request)

        transfer_list, transfer_list_with_category = prepareTransferJSONdata(user_json_data['transfer_list'])
        model_transfer_list = get_model_list(transfer_list_with_category, headers, self.request)
        # transfer_list_table_data, transfer_list_count = prepareTransferTabledata(transfer_list)
        # self.extra_context['transfer_list_table_data'] = transfer_list_table_data
        # self.extra_context['transfer_list_count'] = transfer_list_count
        self.extra_context['transfer_list'] = transfer_list
        self.extra_context['stripped_transfer_list'] = [right['right'] for right in transfer_list_with_category]
        print(self.extra_context.get('stripped_transfer_list'))
        self.extra_context['model_transfer_list'] = model_transfer_list
        self.extra_context['transfer_form'] = ApplyRightForm

        delete_list = user_json_data['delete_list']
        delete_list, delete_list_with_category = prepareDeleteJSONdata(delete_list)
        model_delete_list = get_model_list(delete_list_with_category, headers, self.request)
        delete_list_table_data, delete_list_count = prepareTrashTableData(delete_list)
        # self.extra_context['delete_list_table_data'] = delete_list_table_data
        # self.extra_context['delete_list_count'] = delete_list_count

        self.extra_context['delete_list'] = delete_list
        self.extra_context['stripped_delete_list'] = [right['right'] for right in delete_list_with_category]
        print(self.extra_context.get('stripped_delete_list'))
        self.extra_context['model_delete_list'] = model_delete_list
        self.extra_context['delete_form'] = DeleteRightForm

        self.extra_context['jsondata'] = user_json_data

        # afs = user_json_data['children']
        # data, gf_count, tf_count = prepareTableData(user, roles, afs, headers)

        self.extra_context['user_identity'] = user_json_data['identity']
        self.extra_context['user_first_name'] = user_json_data['first_name']
        self.extra_context['user_name'] = user_json_data['name']
        self.extra_context['user_department'] = user_json_data['department']
        self.extra_context['role_count'] = self.request.session.get('role_count')
        self.extra_context['af_count'] = self.request.session.get('af_count')
        self.extra_context['gf_count'] = self.request.session.get('gf_count')
        self.extra_context['tf_count'] = self.request.session.get('tf_count')

        return []


def get_model_right(comp_user, type, pk, request):
    '''
        method for getting right-model-data for display in my_requests and request_pool
    :param comp_user:
    :param type:
    :param pk:
    :param request:
    :return:
    '''
    if type == 'AF':
        model = get_af_by_key(pk, get_headers(request), request)
        model['right_description'] = model.pop('af_description')
    if type == 'GF':
        model = get_gf_by_key(pk, get_headers(request), request)
        model['right_description'] = model.pop('gf_description')
    if type == 'TF':
        model = get_tf_by_key(pk, get_headers(request), request)
        model['right_description'] = model.pop('tf_description')
    return model


def get_right_from_list(comp_user, type, right, rights):
    '''
        method used by my_requests and request_pool for finding specific right in a list and
        preparing right_data for display as circlePacking
    :param comp_user:
    :param type:
    :param right:
    :param rights:
    :return:
    '''
    for af in rights:
        if type == 'AF':
            if af['af_name'] == right:
                af['name'] = af.pop('af_name')
                af['children'] = af.pop('gfs')
                af['model_right_pk'] = af.pop('model_af_pk')
                for gf in af['children']:
                    gf['name'] = gf.pop('gf_name')
                    gf['children'] = gf.pop('tfs')
                    for tf in gf['children']:
                        tf['name'] = tf.pop('tf_name')
                        tf['size'] = 2000
                return af
        if type == 'GF':
            for gf in af['gfs']:
                if gf['gf_name'] == right:
                    gf['name'] = gf.pop('gf_name')
                    gf['children'] = gf.pop('tfs')
                    gf['model_right_pk'] = gf.pop('model_gf_pk')
                    for tf in gf['children']:
                        tf['name'] = tf.pop('tf_name')
                        tf['size'] = 2000
                    return gf
        if type == 'TF':
            for gf in af['gfs']:
                for tf in gf['tfs']:
                    if tf['tf_name'] == right:
                        tf['name'] = tf.pop('tf_name')
                        tf['size'] = 2000
                        tf['model_right_pk'] = tf.pop('model_tf_pk')
                        return tf


def get_model_list(transfer_list_with_category, headers, request):
    '''
        method for building up list of model-rights to some rights-list(transfer-, delete-, userright-)
    :param transfer_list_with_category:
    :param headers:
    :param request:
    :return:
    '''
    model_list = []
    for right in transfer_list_with_category:
        model = None
        if right['type'] == 'af':
            model = get_af_by_key(pk=right['right']['model_af_pk'], headers=headers, request=request)
            model['right_name'] = model.pop('af_name')
            model['description'] = model.pop('af_description')
        if right['type'] == 'gf':
            model = get_gf_by_key(pk=right['right']['model_gf_pk'], headers=headers, request=request)
            model['right_name'] = model.pop('gf_name')
            model['description'] = model.pop('gf_description')
        if right['type'] == 'tf':
            model = get_tf_by_key(pk=right['right']['model_tf_pk'], headers=headers, request=request)
            model['right_name'] = model.pop('tf_name')
            model['description'] = model.pop('tf_description')
        model['type'] = right['type'].upper()
        model_list.append(model)
    return model_list


def prepareTransferJSONdata(user_json_data,request,headers):
    '''
    method to prepare transferlist-data for display as circlepacking
    :param transfer_json_data:
    :return:
    '''
    transfer_graph_data = {"children": []}
    transfer_list_with_category = []
    single_rights_count = 0
    old_plattform = None
    for e in user_json_data['userid_name']:
        user = get_by_url(e, headers)
        user['name'] = user['userid']
        user['children'] = []
        user_userid_combination = get_full_user_userid_name_combination(headers, user_json_data['id'],
                                                                   user['id'], request)
        #user_userid_combination = get_user_userid_name_combination(headers, user_json_data['id'],
        #                                                           user['id'], request)
        user['user_userid_combi_id'] = user_userid_combination[0]['id']
        transfer_graph_data['children'].append(user)
        for rolle in user_userid_combination[0]['transfer_list']:
            #rolle = get_by_url(rolle, headers)
            rolle_details = rolle['model_rolle_id']
            #rolle_details = get_by_url(rolle['model_rolle_id'], headers)
            rolle['name'] = rolle_details['rollenname']
            rolle['description'] = rolle_details['rollenbeschreibung']
            rolle['children'] = []
            user['children'].append(rolle)
            af_old = None
            for af in rolle['applied_afs']:
                #af = get_by_url(af, headers)
                if af['applied_gfs']:
                    af_details = af['model_af_id']
                    #af_details = get_by_url(af['model_af_id'], headers)
                    af['name'] = af_details['af_name']
                    af['children'] = []
                    rolle['children'].append(af)

                    gf_old = None
                    for gf in af['applied_gfs']:
                        #gf = get_by_url(gf, headers)
                        if gf['applied_tfs']:
                            gf_details = gf['model_gf_id']
                            #gf_details = get_by_url(gf['model_gf_id'], headers)
                            gf['name'] = gf_details['name_gf_neu']
                            gf['children'] = []
                            af['children'].append(gf)

                            for tf in gf['applied_tfs']:
                                #tf = get_by_url(tf, headers)
                                tf_details = tf['model_tf_id']
                                #tf_details = get_by_url(tf['model_tf_id'], headers)
                                tf['name'] = tf_details['tf']
                                tf['size'] = 3000
                                gf['children'].append(tf)
                                single_rights_count += 1
                                if tf_details['plattform'] != old_plattform:
                                    plattform = get_by_url(tf_details['plattform'], headers)
                                    old_plattform = tf_details['plattform']
                                hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                                tf['color'] = hslColor
                                af_applied = None
                                tf['description'] = tf_details['tf_beschreibung']
                                if tf['description'] is None:
                                    tf['description'] = "Keine Beschreibung vorhanden!"
                                if tf_details['datum'] is None:
                                    af_applied = ""
                                else:
                                    af_applied = tf_details['datum']
                                if af['name'] != af_old:
                                    af_description_helper = get_af_description_from_Tblrechteneuvonimport(user['name'],
                                                                                                          af['name'],
                                                                                                          gf['name'],
                                                                                                          tf['name'],
                                                                                                          headers)
                                    if not af_description_helper:
                                        af['description'] = "Keine Beschreibung vorhanden!"
                                    else:
                                        af['description'] = af_description_helper[0]['af_beschreibung']
                                    af_old = af['name']
                                if gf['name'] != gf_old:
                                    if not tf_details['gf_beschreibung']:
                                        gf['description'] = "Keine Beschreibung vorhanden!"
                                    else:
                                        gf['description'] = tf_details['gf_beschreibung']
                                    gf_old = gf['name']

    return transfer_graph_data, transfer_list_with_category, single_rights_count


def prepareTransferTabledata(transfer_list):
    '''
    prepares transfer-data for display as table
    :param transfer_list:
    :return:
    '''
    tfList = []
    gfList = []
    afList = []
    for af in transfer_list:
        for gf in af['children']:
            for tf in gf['children']:
                tfList.append(tf['name'])
                gfList.append(gf['name'])
                afList.append(af['name'])

    data = zip(tfList, gfList, afList)
    lis_data = list(data)
    return lis_data, len(lis_data)


def get_delete_list_counts(list):
    '''
    counts elements in delete list to keep correct count for display
    :param list:
    :return:
    '''
    del_af_count = 0
    del_gf_count = 0
    del_tf_count = 0
    for right in list:
        if right['type'] == 'af':
            af = right['right']
            del_af_count += 1
            gfs = af['children']
            del_gf_count += len(gfs)
            for gf in gfs:
                tfs = gf['children']
                del_tf_count += len(tfs)
        elif right['type'] == "gf":
            gf = right['right']
            del_gf_count += 1
            tfs = gf['children']
            del_tf_count += len(tfs)
        elif right['type'] == "tf":
            del_tf_count += 1

    return del_af_count, del_gf_count, del_tf_count


'''
    def autocompleteModel(self, request):
        if request.is_ajax():
            q = request.GET.get('term', '').capitalize()
            search_qs = User.objects.filter(name__startswith=q)
            results = []
            print(q)
            for r in search_qs:
                results.append(r.FIELD)
            data = json.dumps(results)
        else:
            data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
'''


def setViewMode(request, extra_context):
    '''
        reads viewmode out of GET-request for any-view wher viewmode is switchable between graphic- and table- mode
    :param request:
    :param extra_context:
    :return:
    '''
    if request.GET.keys().__contains__("view_mode"):
        extra_context['view_mode'] = request.GET['view_mode']
    else:
        extra_context['view_mode'] = 'Graphische Ansicht'


def prepareTrashTableData(afs):
    '''
    prepares trash-data for display as table
    :param afs:
    :return:
    '''
    tfList = []
    gfList = []
    afList = []

    for af in afs:
        gfs = af['children']
        for gf in gfs:
            tfs = gf['children']
            for tf in tfs:
                tfList.append(tf['name'])
                gfList.append(gf['name'])
                afList.append(af['name'])

    data = zip(tfList, gfList, afList)
    lis_data = list(data)
    return lis_data, len(lis_data)


def prepareTableData(user, roles, afs, headers):
    '''
    prepares user-rights-data for display as table
    :param user:
    :param roles:
    :param afs:
    :param headers:
    :return:
    '''
    tfList = []
    gfList = []
    afList = []
    gf_count = 0
    for af in afs:
        gfs = af['children']
        gf_count += len(gfs)
        for gf in gfs:
            tfs = gf['children']
            for tf in tfs:
                tfList.append(tf['name'])
                gfList.append(gf['name'])
                afList.append(af['name'])

    data = zip(tfList, gfList, afList)
    tf_count = len(tfList)
    return list(data), gf_count, tf_count


def get_headers(request):
    '''
    gets headers for API-Requests
        loggedinusertoken for authentification with the drf-framework
    :param request:
    :return:
    '''
    logged_in_user_token = request.user.auth_token
    headers = {'Authorization': 'Token ' + logged_in_user_token.key}
    return headers


def get_last_import(headers):
    '''
    :param headers:
    :return:
    '''
    url = docker_container_ip + '/api/letzte_imports/?specify=%s' % 'latest'
    res = requests.get(url, headers=headers)
    li_json = res.json()
    if 'results' in li_json:
        li_json = li_json['results']
    elif 'detail' in li_json:
        print(li_json['detail'])
        raise ConnectionError(li_json['detail'])
    return li_json


def get_tf_applications(headers, request):
    '''
        Get-Method for API-Requests
        gets tf_applications-data for legend
    :param headers:
    :param request:
    :return:
    '''
    # url = 'http://' + request.get_host() + '/tf_applications/'
    url = docker_container_ip + '/api/plattformen/'
    tf_applications = requests.get(url, headers=headers)
    tf_applications_json = tf_applications.json()
    if 'results' in tf_applications_json:
        tf_app_json = tf_applications_json['results']
        while tf_applications_json['next'] is not None:
            tf_applications = requests.get(tf_applications_json['next'], headers=headers)
            tf_applications_json = tf_applications.json()
            tf_app_json += tf_applications_json['results']
    elif 'detail' in tf_applications_json:
        print(tf_applications_json['detail'])
        raise ConnectionError(tf_applications_json['detail'])
    return tf_app_json


def get_af_by_key(pk, headers, request):
    '''
        Get-Method for API-Requests
        gets specific AF by key
    :param headers:
    :param request:
    :return:
    '''
    # url = 'http://' + request.get_host() + '/afs/%d' % pk
    url = docker_container_ip + '/afs/%d' % pk
    af_json = requests.get(url, headers=headers).json()
    if 'results' in af_json:
        af_json = af_json['results']
    elif 'detail' in af_json:
        print(af_json['detail'])
        raise ConnectionError(af_json['detail'])
    return af_json


def get_gf_by_key(pk, headers, request):
    '''
            Get-Method for API-Requests
            gets specific GF by key
        :param headers:
        :param request:
        :return:
        '''
    # url = 'http://' + request.get_host() + '/gfs/%d' % pk
    url = docker_container_ip + '/gfs/%d' % pk
    gf_json = requests.get(url, headers=headers).json()
    if 'results' in gf_json:
        gf_json = gf_json['results']
    elif 'detail' in gf_json:
        print(gf_json['detail'])
        raise ConnectionError(gf_json['detail'])
    return gf_json


def get_tf_by_key(pk, headers, request):
    '''
            Get-Method for API-Requests
            gets specific TF by key
        :param headers:
        :param request:
        :return:
        '''
    # url = 'http://' + request.get_host() + '/tfs/%d' % pk
    url = docker_container_ip + '/tfs/%d' % pk
    tf_json = requests.get(url, headers=headers).json()
    if 'results' in tf_json:
        tf_json = tf_json['results']
    elif 'detail' in tf_json:
        print(tf_json['detail'])
        raise ConnectionError(tf_json['detail'])
    return tf_json


def get_user_model_rights_by_key(pk, headers, request):
    '''
        Get-Method for API-Requests
        gets usermodelrights for data-compare with userrights
    :param headers:
    :param request:
    :return:
    '''
    # url = 'http://' + request.get_host() + '/usermodelrights/%d' % pk
    url = docker_container_ip + '/usermodelrights/%d' % pk
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_user_by_key(pk, headers, request):
    '''
        Get-Method for API-Requests
        gets specific User by xvNumber as key
    :param headers:
    :param request:
    :return:
    '''
    # url = 'http://' + request.get_host() + '/users/%s' % pk
    url = docker_container_ip + '/api/users/%s' % pk
    res = requests.get(url, headers=headers)
    json = res.json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_user_by_name(xvnumber, headers, request):
    '''
        Get-Method for API-Requests
        gets specific User by xvNumber as key
    :param headers:
    :param request:
    :return:
    '''
    # url = 'http://' + request.get_host() + '/users/%s' % pk
    url = docker_container_ip + '/api/users/?xvnumber=%s' % xvnumber
    res = requests.get(url, headers=headers)
    json = res.json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_changerequests(headers, request):
    '''
        Get-Method for API-Requests
        gets changerequests for display in requestpool
    :param headers:
    :param request:
    :return:
    '''
    # url = 'http://' + request.get_host() + '/changerequests/'
    url = docker_container_ip + '/changerequests/'
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_tfs(headers, request):
    '''
        Get-Method for API-Requests
        gets tfs
    :param headers:
    :param request:
    :return:
    '''
    # url = 'http://' + request.get_host() + '/tfs/'
    url = docker_container_ip + '/tfs/'
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_user_roles(headers, user_pk, request):
    '''
    :param headers:
    :param user_pk:
    :param request:
    :return:
    '''
    url = docker_container_ip + '/api/userhatrollen/'
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_user_userid_name_combination(headers, user_pk, userid_name_pk, request):
    '''
    :param headers:
    :param user_pk:
    :param userid_name_pk:
    :param request:
    :return:
    '''
    url = docker_container_ip + '/api/userhatuseridundnamen/?user_pk='+str(user_pk)+'&userid_name_pk='+str(userid_name_pk)
    res = requests.get(url, headers=headers)
    json = res.json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_full_user_userid_name_combination(headers, user_pk, userid_name_pk, request):
    '''
    :param headers:
    :param user_pk:
    :param userid_name_pk:
    :param request:
    :return:
    '''
    url = docker_container_ip + '/api/fulluserhatuseridundnamen/?user_pk='+str(user_pk)+'&userid_name_pk='+str(userid_name_pk)
    res = requests.get(url, headers=headers)
    json = res.json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_by_url(url, headers):
    '''
        Get-Method for API-Requests
        get anything from API by url
    :param headers:
    :param request:
    :return:
    '''
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_AFGF_by_af_name(af_name, headers):
    url = docker_container_ip + '/api/afgfs/?af_name=' + af_name
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_tf_aus_gesamt_by_user_name_af_name_gf_name(userid_name, af_name, gf_name, headers):
    url = docker_container_ip + '/api/gesamte/?userid_name=' + userid_name.__str__() + '&af_name=' + af_name + '&gf_name=' + gf_name
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_af_description_from_Tblrechteneuvonimport(user, af, gf, tf, headers):
    url = docker_container_ip + '/api/rechteneuvonimport/?userid_name=' + user + '&af_name=' + af + '&gf_name=' + gf + '&tf_name=' + tf
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def patch_user_last_rights_update(user_id, last_rights_update, headers):
    url = docker_container_ip + '/api/users/'
    data = {"userid":user_id, "last_rights_update": last_rights_update}
    try:
        res = requests.patch(url, data=data, headers=headers)
        print("User last_rights_update-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von af_gfs")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def patch_af_gfs(af_id, gf_id, headers):
    url = docker_container_ip + '/api/afs/'
    data = {"af_id": af_id, "gf_id": gf_id}
    try:
        requests.patch(url, data=data, headers=headers)
        print("AF-GFS-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von af_gfs")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def patch_gf_tfs(gf_id, tf_id, headers):
    url = docker_container_ip + '/api/afgfs/'
    data = {"gf_id": gf_id, "tf_id": tf_id}
    try:
        requests.patch(url, data=data, headers=headers)
        print("GF-TFS-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von gf_tfs")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_applied_role(role,uhatuid,headers):
    url = docker_container_ip + '/api/appliedroles/'
    data = {'model_rolle_id':role['rollenid'],'userHatUserID_id':uhatuid['id']}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("applied_role_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von applied_role")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_applied_af(af,applied_role,headers):
    url = docker_container_ip + '/api/appliedafs/'
    data = {'model_af_id':af['id'],'applied_role_id':applied_role['id']}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("applied_af_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von applied_af")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_applied_gf(gf,applied_af,headers):
    url = docker_container_ip + '/api/appliedgfs/'
    data = {'model_gf_id':gf['id'],'applied_af_id':applied_af['id']}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("applied_gf_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von applied_gf")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_applied_tf(tf,applied_gf,headers):
    url = docker_container_ip + '/api/appliedtfs/'
    data = {'model_tf_id':tf['id'],'applied_gf_id':applied_gf['id']}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("applied_tf_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von applied_tf")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def patch_userhatuseridundnamen_rollen(userhatuseridundname_id, rollen_id, headers):
    url = docker_container_ip + '/api/userhatuseridundnamen/'
    data = {"userhatuseridundname_id": userhatuseridundname_id, "rollen_id": rollen_id}
    try:
        res = requests.patch(url, data=data, headers=headers)
        print("UserHatUseridundnamen-Rollen-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von userhatuseridundnamen_rollen")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def patch_applied_rolle_applied_afs(applied_rolle_id, applied_af_id, headers):
    url = docker_container_ip + '/api/appliedroles/'
    data = {"applied_rolle_id": applied_rolle_id, "applied_af_id": applied_af_id}
    try:
        res = requests.patch(url, data=data, headers=headers)
        print("UserHatUseridundnamen-Rollen-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von userhatuseridundnamen_rollen")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def patch_applied_af_applied_gfs(applied_af_id, applied_gf_id, headers):
    url = docker_container_ip + '/api/appliedafs/'
    data = {"applied_af_id": applied_af_id, "applied_gf_id": applied_gf_id}
    try:
        requests.patch(url, data=data, headers=headers)
        print("AF-GFS-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von af_gfs")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def patch_applied_gf_applied_tfs(applied_gf_id, applied_tf_id, headers):
    url = docker_container_ip + '/api/appliedgfs/'
    data = {"applied_gf_id": applied_gf_id, "applied_tf_id": applied_tf_id}
    try:
        requests.patch(url, data=data, headers=headers)
        print("GF-TFS-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von gf_tfs")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def update_af_gfs(af,headers):
    afgfs_iter = iter(af['gfs'])
    gfs = get_AFGF_by_af_name(af['af_name'],headers)
    for gf in gfs:
        try:
            next_gf = next(afgfs_iter)
            if next_gf==gf['url']:
                print('found gf')
            else:
                full_check_iterator = iter(af['gfs'])
                try:
                    next_full_check_iter = next(full_check_iterator)
                    while next_full_check_iter:
                        if next_full_check_iter == gf['url']:
                            # update_personal_af_gfs(af, applied_af, headers)
                            break
                        else:
                            next_full_check_iter = next(full_check_iterator)
                except StopIteration:
                    patch_af_gfs(af['id'], gf['id'], headers)
        except StopIteration:
            patch_af_gfs(af['id'],gf['id'],headers)


def update_gf_tfs(gf,af,user,headers):
    gftfs_iter = iter(gf['tfs'])
    tfs = get_tf_aus_gesamt_by_user_name_af_name_gf_name(user['id'], af['af_name'], gf['name_gf_neu'], headers)
    for tf in tfs:
        try:
            next_tf = next(gftfs_iter)
            if next_tf==tf['url']:
                print('found tf')
            else:
                full_check_iterator = iter(gf['tfs'])
                try:
                    next_full_check_iter = next(full_check_iterator)
                    while next_full_check_iter:
                        if next_full_check_iter == tf['url']:
                            print('found tf')
                            break
                        else:
                            next_full_check_iter = next(full_check_iterator)
                except StopIteration:
                    patch_gf_tfs(gf['id'], tf['id'], headers)
        except StopIteration:
            patch_gf_tfs(gf['id'],tf['id'],headers)
    return tfs


def update_personal_gf_tfs(gf, tfs, applied_gf, headers):
    print(gf)
    print(applied_gf)
    applied_tfs_iter = iter(applied_gf['applied_tfs'])
    for tf in gf['tfs']:
        tf = get_by_url(tf,headers)
        if tf in tfs:
            try:
                next_applied_tf =next(applied_tfs_iter)
                applied_tf = next_applied_tf
                #applied_tf = get_by_url(next_applied_tf, headers)
                if applied_tf['model_tf_id']['url'] == tf['url']:
                    print('found personal tf')
                else:
                    full_check_iterator = iter(applied_gf['applied_tfs'])
                    try:
                        next_full_check_iter = next(full_check_iterator)
                        while next_full_check_iter:
                            applied_tf = next_full_check_iter
                            #applied_tf = get_by_url(next_full_check_iter, headers)
                            if applied_tf['model_tf_id']['url'] == tf['url']:
                                print('found personal tf')
                                break
                            else:
                                next_full_check_iter = next(full_check_iterator)
                    except StopIteration:
                        res = create_applied_tf(tf, applied_tf, headers)
                        applied_tf = json.loads(res.text)
                        patch_applied_gf_applied_tfs(applied_gf['id'], applied_tf['id'], headers)
            except StopIteration:
                res = create_applied_tf(tf, applied_gf, headers)
                applied_tf = json.loads(res.text)
                patch_applied_gf_applied_tfs(applied_gf['id'], applied_tf['id'], headers)

    return


def update_personal_af_gfs(af, user, applied_af, headers):
    print(af)
    print(applied_af)
    applied_gfs_iter = iter(applied_af['applied_gfs'])
    for gf in af['gfs']:
        gf = get_by_url(gf,headers)
        tfs = update_gf_tfs(gf, af, user, headers)
        try:
            next_applied_gf =next(applied_gfs_iter)
            applied_gf = next_applied_gf
            #applied_gf = get_by_url(next_applied_gf, headers)
            if applied_gf['model_gf_id']['url'] == gf['url']:
                print('found personal gf')
                update_personal_gf_tfs(gf, tfs, applied_gf, headers)
            else:
                full_check_iterator = iter(applied_af['applied_gfs'])
                try:
                    next_full_check_iter = next(full_check_iterator)
                    while next_full_check_iter:
                        applied_gf = next_full_check_iter
                        #applied_gf = get_by_url(next_full_check_iter, headers)
                        if applied_gf['model_gf_id']['url'] == gf['url']:
                            print('found personal gf')
                            update_personal_gf_tfs(gf, tfs, applied_gf, headers)
                            break
                        else:
                            next_full_check_iter = next(full_check_iterator)
                except StopIteration:
                    res = create_applied_gf(gf, applied_af, headers)
                    applied_gf = json.loads(res.text)
                    patch_applied_af_applied_gfs(applied_af['id'], applied_gf['id'], headers)
                    update_personal_gf_tfs(gf, tfs, applied_gf, headers)
        except StopIteration:
            res = create_applied_gf(gf, applied_af, headers)
            applied_gf = json.loads(res.text)
            patch_applied_af_applied_gfs(applied_af['id'], applied_gf['id'], headers)
            update_personal_gf_tfs(gf, tfs, applied_gf, headers)
    return


def update_personal_role_afs(role, user ,applied_role, headers):
    print(role)
    print(applied_role)
    applied_afs_iter = iter(applied_role['applied_afs'])
    for af in role['afs']:
        af = get_by_url(af,headers)
        update_af_gfs(af, headers)
        try:
            next_applied_af =next(applied_afs_iter)
            applied_af = next_applied_af
            #applied_af = get_by_url(next_applied_af, headers)
            if applied_af['model_af_id']['url'] == af['url']:
                print('found personal af')
                update_personal_af_gfs(af, user ,applied_af, headers)
            else:
                full_check_iterator = iter(applied_role['applied_afs'])
                try:
                    next_full_check_iter = next(full_check_iterator)
                    while next_full_check_iter:
                        applied_af = next_full_check_iter
                        #applied_af = get_by_url(next_full_check_iter, headers)
                        if applied_af['model_af_id']['url'] == af['url']:
                            print('found personal af')
                            update_personal_af_gfs(af,  user ,applied_af, headers)
                            break
                        else:
                            next_full_check_iter = next(full_check_iterator)
                except StopIteration:
                    res = create_applied_af(af, applied_role, headers)
                    applied_af = json.loads(res.text)
                    patch_applied_rolle_applied_afs(applied_role['id'], applied_af['id'], headers)
                    update_personal_af_gfs(af,  user ,applied_af, headers)
        except StopIteration:
            res = create_applied_af(af, applied_role, headers)
            applied_af = json.loads(res.text)
            patch_applied_rolle_applied_afs(applied_role['id'], applied_af['id'], headers)
            update_personal_af_gfs(af,  user ,applied_af, headers)
    return


def update_personal_right_models(user_json_data, headers, request):
    print(user_json_data)
    for user in user_json_data['userid_name']:
        userid_name_data = get_by_url(user, headers)
        user_userid_combination = get_full_user_userid_name_combination(headers,user_json_data['id'],userid_name_data['id'],request)
        #user_userid_combination = get_user_userid_name_combination(headers,user_json_data['id'],userid_name_data['id'],request)
        print(userid_name_data)
        print(user_userid_combination)
        applied_role_iter = iter(user_userid_combination[0]['rollen'])
        for role in userid_name_data['rollen']:
            role = get_by_url(role, headers)
            try:
                next_applied_role = next(applied_role_iter)
                applied_role = next_applied_role
                #applied_role = get_by_url(next_applied_role, headers)

                if role['url'] == applied_role['model_rolle_id']['url']:
                    print('found personal role')
                    update_personal_role_afs(role, userid_name_data, applied_role, headers)
                else:
                    full_check_iterator = iter(user_userid_combination[0]['rollen'])
                    try:
                        next_full_check_iter = next(full_check_iterator)
                        while next_full_check_iter:
                            applied_role = next_full_check_iter
                            #applied_role = get_by_url(next_full_check_iter, headers)
                            if role['url'] == applied_role['model_rolle_id']['url']:
                                print('found personal role')
                                update_personal_role_afs(role, userid_name_data, applied_role, headers)
                                break
                            else:
                                next_full_check_iter = next(full_check_iterator)
                    except StopIteration:
                        res = create_applied_role(role, user_userid_combination[0], headers)
                        applied_role = json.loads(res.text)
                        patch_userhatuseridundnamen_rollen(user_userid_combination[0]['id'], applied_role['id'],
                                                           headers)
                        update_personal_role_afs(role, userid_name_data, applied_role, headers)
            except StopIteration:
                res = create_applied_role(role,user_userid_combination[0],headers)
                applied_role = json.loads(res.text)
                patch_userhatuseridundnamen_rollen(user_userid_combination[0]['id'],applied_role['id'],headers)
                update_personal_role_afs(role, userid_name_data, applied_role, headers)

    return


def prepareJSONdata(identity, user_json_data, compareUser, headers, request):
    '''
    prepares Data for display as circlePacking and scatterplot
    :param identity:
    :param user_json_data:
    :param compareUser:
    :param headers:
    :param request:
    :return:
    '''
    scatterData = []
   # user_json_data['children'] = user_json_data.pop('user_afs')
    user_detail_data = []
    graph_data = dict()
    graph_data['children'] = []
    old_plattform = None
    counts = {'user': 0, 'roles': 0, 'afs': 0, 'gfs': 0, 'tfs': 0, }

    for e in user_json_data['userid_name']:
        user = get_by_url(e, headers)
        user['name'] = user['userid']
        user['children'] = []
        counts['user'] += 1
        #user_userid_combination = get_user_userid_name_combination(headers, user_json_data['id'],
        #                                                         user['id'], request)
        user_userid_combination = get_full_user_userid_name_combination(headers, user_json_data['id'],
                                                                 user['id'], request)
        user['user_userid_combi_id'] = user_userid_combination[0]['id']
        graph_data['children'].append(user)
        for rolle in user_userid_combination[0]['rollen']:
            #rolle = get_by_url(rolle, headers)
            if rolle['applied_afs']:
                rolle_details = rolle['model_rolle_id']
                #rolle_details = get_by_url(rolle['model_rolle_id'],headers)
                rolle['name'] = rolle_details['rollenname']
                rolle['description'] = rolle_details['rollenbeschreibung']
                rolle['children'] = []
                user['children'].append(rolle)
                counts['roles'] += 1
                af_old = None
                for af in rolle['applied_afs']:
                    #af = get_by_url(af, headers)
                    if af['applied_gfs']:
                        af_details = af['model_af_id']
                        #af_details = get_by_url(af['model_af_id'], headers)
                        af['name'] = af_details['af_name']
                        af['children'] = []
                        rolle['children'].append(af)

                        gf_old = None
                        for gf in af['applied_gfs']:
                            #gf = get_by_url(gf, headers)
                            if gf['applied_tfs']:
                                gf_details = gf['model_gf_id']
                                #gf_details = get_by_url(gf['model_gf_id'], headers)
                                gf['name'] = gf_details['name_gf_neu']
                                gf['children'] = []
                                counts['gfs'] += 1
                                af['children'].append(gf)

                                old_plattform = None
                                for tf in gf['applied_tfs']:
                                    #tf = get_by_url(tf, headers)
                                    tf_details = tf['model_tf_id']
                                    #tf_details = get_by_url(tf['model_tf_id'], headers)
                                    tf['name'] = tf_details['tf']
                                    tf['size'] = 3000
                                    gf['children'].append(tf)
                                    counts['tfs'] += 1
                                    if tf_details['plattform'] != old_plattform:
                                        plattform = get_by_url(tf_details['plattform'], headers)
                                        old_plattform = tf_details['plattform']
                                    hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                                    tf['color'] = hslColor
                                    af_applied = None
                                    tf['description'] = tf_details['tf_beschreibung']
                                    if tf['description'] is None:
                                        tf['description'] = "Keine Beschreibung vorhanden!"
                                    if tf_details['datum'] is None:
                                        af_applied = ""
                                    else:
                                        af_applied = tf_details['datum']
                                    scatterData.append(
                                        {"name": tf['name'], "gf_name": gf['name'], "af_name": af['name'],
                                         "role": rolle['name'],
                                         "user": user['name'], "plattform": plattform["tf_technische_plattform"],
                                         "af_applied": af_applied, "color": hslColor})
                                    if af['name'] != af_old:
                                        counts['afs'] += 1
                                        af_description_helper = get_af_description_from_Tblrechteneuvonimport(user['name'],
                                                                                                              af['name'],
                                                                                                              gf['name'],
                                                                                                              tf['name'],
                                                                                                              headers)
                                        if not af_description_helper:
                                            af['description'] = "Keine Beschreibung vorhanden!"
                                        else:
                                            af['description'] = af_description_helper[0]['af_beschreibung']
                                        af_old = af['name']
                                    if gf['name'] != gf_old:
                                        if not tf_details['gf_beschreibung']:
                                            gf['description'] = "Keine Beschreibung vorhanden!"
                                        else:
                                            gf['description'] = tf_details['gf_beschreibung']
                                        gf_old = gf['name']
                            if gf in af['children'] and not gf['children']:
                                af['children'].remove(gf)
                    if af in rolle['children'] and not af['children']:
                        rolle['children'].remove(af)
            if not rolle['children']:
                counts['roles'] -= 1
    if not compareUser:
        scatterData.sort(key=lambda r: r["af_applied"])
        i = 0
        for e in scatterData:
            e["index"] = i
            i += 1
    return graph_data, scatterData, counts


def prepareDeleteJSONdata(user_json_data, request, headers):
    '''
    prepare delete_list for display as circlepacking
    :param delete_list:
    :return:
    '''
    delete_graph_data = {"children": []}
    delete_list_with_category = []
    single_rights_count = 0
    old_plattform = None
    for e in user_json_data['userid_name']:
        user = get_by_url(e, headers)
        user['name'] = user['userid']
        user['children'] = []
        user_userid_combination = get_full_user_userid_name_combination(headers, user_json_data['id'],
                                                                   user['id'], request)
        #user_userid_combination = get_user_userid_name_combination(headers, user_json_data['id'],
        #                                                           user['id'], request)
        user['user_userid_combi_id'] = user_userid_combination[0]['id']
        delete_graph_data['children'].append(user)
        for rolle in user_userid_combination[0]['delete_list']:
            #rolle = get_by_url(rolle, headers)
            rolle_details = rolle['model_rolle_id']
            #rolle_details = get_by_url(rolle['model_rolle_id'], headers)
            rolle['name'] = rolle_details['rollenname']
            rolle['description'] = rolle_details['rollenbeschreibung']
            rolle['children'] = []
            user['children'].append(rolle)
            af_old = None
            for af in rolle['applied_afs']:
                #af = get_by_url(af, headers)
                if af['applied_gfs']:
                    af_details = af['model_af_id']
                    #af_details = get_by_url(af['model_af_id'], headers)
                    af['name'] = af_details['af_name']
                    af['children'] = []
                    rolle['children'].append(af)

                    gf_old = None
                    for gf in af['applied_gfs']:
                        #gf = get_by_url(gf, headers)
                        if gf['applied_tfs']:
                            gf_details = gf['model_gf_id']
                            #gf_details = get_by_url(gf['model_gf_id'], headers)
                            gf['name'] = gf_details['name_gf_neu']
                            gf['children'] = []
                            af['children'].append(gf)

                            for tf in gf['applied_tfs']:
                                #tf = get_by_url(tf, headers)
                                tf_details = tf['model_tf_id']
                                #tf_details = get_by_url(tf['model_tf_id'], headers)
                                tf['name'] = tf_details['tf']
                                tf['size'] = 3000
                                gf['children'].append(tf)
                                single_rights_count += 1
                                if tf_details['plattform'] != old_plattform:
                                    plattform = get_by_url(tf_details['plattform'], headers)
                                    old_plattform = tf_details['plattform']
                                hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                                tf['color'] = hslColor
                                af_applied = None
                                tf['description'] = tf_details['tf_beschreibung']
                                if tf['description'] is None:
                                    tf['description'] = "Keine Beschreibung vorhanden!"
                                if tf_details['datum'] is None:
                                    af_applied = ""
                                else:
                                    af_applied = tf_details['datum']
                                if af['name'] != af_old:
                                    af_description_helper = get_af_description_from_Tblrechteneuvonimport(user['name'],
                                                                                                          af['name'],
                                                                                                          gf['name'],
                                                                                                          tf['name'],
                                                                                                          headers)
                                    if not af_description_helper:
                                        af['description'] = "Keine Beschreibung vorhanden!"
                                    else:
                                        af['description'] = af_description_helper[0]['af_beschreibung']
                                    af_old = af['name']
                                if gf['name'] != gf_old:
                                    if not tf_details['gf_beschreibung']:
                                        gf['description'] = "Keine Beschreibung vorhanden!"
                                    else:
                                        gf['description'] = tf_details['gf_beschreibung']
                                    gf_old = gf['name']

    return delete_graph_data, delete_list_with_category, single_rights_count


class TblRollenViewSet(viewsets.ModelViewSet):
    '''
        API-Rollen ViewSet
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = TblRollenSerializer

    def get_queryset(self):
        return TblRollen.objects.all()


class TblUebersichtAfGfsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblUebersichtAfGfsSerializer

    def get_queryset(self):
        if 'af_name' in self.request.GET:
            af_name = self.request.GET['af_name']
            return TblUebersichtAfGfs.objects.filter(name_af_neu=af_name).order_by('id')

        return TblUebersichtAfGfs.objects.all()

    def patch(self, request, *args, **kwargs):
        print("in UebersichtAfGfs API-Viewset-PATCH-Method")
        pk = request.POST['gf_id']
        gf_to_update = TblUebersichtAfGfs.objects.get(id=pk)
        update_tfs = gf_to_update.tfs
        update_tfs.add(request.POST['tf_id'])
        return Response(status=status.HTTP_201_CREATED)


class TblOrgaViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblOrgaSerializer

    def get_queryset(self):
        return TblOrga.objects.all()


class TblUserIDundNameViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblUserIDundNameSerializer

    def get_queryset(self):
        return TblUserIDundName.objects.all()


class TblPlattformViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblPlattformSerializer

    def get_queryset(self):
        return TblPlattform.objects.all()


class TblGesamtViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblGesamtSerializer

    def get_queryset(self):
        if 'userid_name' in self.request.GET and 'af_name' in self.request.GET and 'gf_name' in self.request.GET:
            userid_name = self.request.GET['userid_name']
            af_name = self.request.GET['af_name']
            gf_name = self.request.GET['gf_name']
            filtered = TblGesamt.objects.filter(userid_name_id=userid_name).filter(enthalten_in_af=af_name) \
                .filter(gf=gf_name).order_by('id')
            return filtered
        return TblGesamt.objects.all()


class TblGesamtHistorieViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblGesamtHistorieSerializer

    def get_queryset(self):
        return TblGesamtHistorie.objects.all()


class TblAflisteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAflisteSerializer

    def get_queryset(self):
        return TblAfliste.objects.all()

    def patch(self, request, *args, **kwargs):
        print("in AfListe API-Viewset-PATCH-Method")
        pk = request.POST['af_id']
        af_to_update = TblAfliste.objects.get(id=pk)
        update_gfs = af_to_update.gfs
        update_gfs.add(request.POST['gf_id'])
        return Response(status=status.HTTP_201_CREATED)


class TblsachgebieteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblsachgebieteSerializer

    def get_queryset(self):
        return Tblsachgebiete.objects.all()


class TblsubsystemeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblsubsystemeSerializer

    def get_queryset(self):
        return Tblsubsysteme.objects.all()


class TblDb2ViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblDb2Serializer

    def get_queryset(self):
        return TblDb2.objects.all()


class TblRacfGruppenViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblRacfGruppenSerializer

    def get_queryset(self):
        return TblRacfGruppen.objects.all()


class TblrechteneuvonimportViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblrechteneuvonimportSerializer

    def get_queryset(self):
        if 'userid_name' in self.request.GET and 'af_name' in self.request.GET and 'gf_name' in self.request.GET \
                and 'tf_name' in self.request.GET:
            userid_name = self.request.GET['userid_name']
            af_name = self.request.GET['af_name']
            gf_name = self.request.GET['gf_name']
            tf_name = self.request.GET['tf_name']
            filtered = Tblrechteneuvonimport.objects.filter(identitaet=userid_name) \
                .filter(af_anzeigename=af_name).filter(gf_name=gf_name).filter(tf_name=tf_name)
            return filtered
        return Tblrechteneuvonimport.objects.all()


class TblrechteamneuViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblrechteamneuSerializer

    def get_queryset(self):
        return Tblrechteamneu.objects.all()


class Qryf3RechteneuvonimportduplikatfreiViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = Qryf3RechteneuvonimportduplikatfreiSerializer

    def get_queryset(self):
        return Qryf3Rechteneuvonimportduplikatfrei.objects.all()


class RACF_RechteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RACF_RechteSerializer

    def get_queryset(self):
        return RACF_Rechte.objects.all()


class Orga_detailsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = Orga_detailsSerializer

    def get_queryset(self):
        return Orga_details.objects.all()


class Letzter_importViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = Letzter_importSerializer

    def get_queryset(self):
        if 'specify' in self.request.GET:
            specify = self.request.GET['specify']
            res = Letzter_import.objects.order_by('-id')[:2]
            return res
        return Letzter_import.objects.all()


class ModellierungViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ModellierungSerializer

    def get_queryset(self):
        return Modellierung.objects.all()


class DirektverbindungenViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DirektverbindungenSerializer

    def get_queryset(self):
        return Direktverbindungen.objects.all()


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        if 'xvnumber' in self.request.GET:
            xvnumber = self.request.GET['xvnumber']
            user = User.objects.filter(username=xvnumber)
            return user
        return User.objects.all()

    def patch(self, request, *args, **kwargs):
        print("in Users API-Viewset-PATCH-Method")
        if 'last_rights_update' in request.POST:
            last_rights_update = request.POST['last_rights_update']
            userid = request.POST['userid']
            user = User.objects.get(id=userid)
            user.last_rights_update = last_rights_update
            user.save()
        return Response(status=status.HTTP_201_CREATED)


class UserHatTblUserIDundNameViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserHatTblUserIDundNameSerializer

    def get_queryset(self):
        if 'user_pk' in self.request.GET and 'userid_name_pk' in self.request.GET:
            user_pk = self.request.GET['user_pk']
            userid_name_pk = self.request.GET['userid_name_pk']
            filtered = UserHatTblUserIDundName.objects.filter(user_name=user_pk) \
                .filter(userid_name_id=userid_name_pk)
            return filtered
        return UserHatTblUserIDundName.objects.all()

    def patch(self, request, *args, **kwargs):
        print("in UserHatTblUserIDundName API-Viewset-PATCH-Method")
        pk = request.POST['userhatuseridundname_id']
        userhatuseridundname_to_update = UserHatTblUserIDundName.objects.get(id=pk)
        update_rollen = userhatuseridundname_to_update.rollen
        update_rollen.add(request.POST['rollen_id'])
        return Response(status=status.HTTP_201_CREATED)


class TblUserhatrolleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblUserhatrolleSerializer

    def get_queryset(self):
        return TblUserhatrolle.objects.all()


class TblRollehatafViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblRollehatafSerializer

    def get_queryset(self):
        return TblRollehataf.objects.all()


class TblAfHatGfViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAfHatGfSerializer

    def get_queryset(self):
        return TblAfHatGf.objects.all()


class TblAppliedRolleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAppliedRolleSerializer

    def get_queryset(self):
        return TblAppliedRolle.objects.all()

    def create(self, request, *args, **kwargs):
        print("In AppliedRoleViewSet-Create")
        serializer = TblAppliedRolleSerializer(data=request.data)
        if serializer.is_valid():
            applied_rolle = serializer.save()
            return Response(data=TblAppliedRolleSerializer(applied_rolle,context={'request':request}).data,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        print("In AppliedRoleViewSet-Patch")
        pk = request.POST['applied_rolle_id']
        applied_rolle_to_update = TblAppliedRolle.objects.get(id=pk)
        update_afs = applied_rolle_to_update.applied_afs
        update_afs.add(request.POST['applied_af_id'])
        return Response(status=status.HTTP_201_CREATED)


    def post(self,request, *args, **kwargs):
        print("In AppliedRoleViewSet-POST")
        return


class TblAppliedAfsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAppliedAfSerializer

    def get_queryset(self):
        return TblAppliedAf.objects.all()

    def create(self, request, *args, **kwargs):
        print("In AppliedAfViewSet-Create")
        serializer = TblAppliedAfSerializer(data=request.data)
        if serializer.is_valid():
            applied_af = serializer.save()
            return Response(data=TblAppliedAfSerializer(applied_af,context={'request':request}).data,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        print("In AppliedAfViewSet-Patch")
        pk = request.POST['applied_af_id']
        applied_af_to_update = TblAppliedAf.objects.get(id=pk)
        update_gfs = applied_af_to_update.applied_gfs
        update_gfs.add(request.POST['applied_gf_id'])
        return Response(status=status.HTTP_201_CREATED)


class TblAppliedGfsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAppliedGfSerializer

    def get_queryset(self):
        return TblAppliedGf.objects.all()

    def create(self, request, *args, **kwargs):
        print("In AppliedGfViewSet-Create")
        serializer = TblAppliedGfSerializer(data=request.data)
        if serializer.is_valid():
            applied_gf = serializer.save()
            return Response(data=TblAppliedGfSerializer(applied_gf,context={'request':request}).data,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        print("In AppliedGfViewSet-Patch")
        pk = request.POST['applied_gf_id']
        applied_gf_to_update = TblAppliedGf.objects.get(id=pk)
        update_tfs = applied_gf_to_update.applied_tfs
        update_tfs.add(request.POST['applied_tf_id'])
        return Response(status=status.HTTP_201_CREATED)


class TblAppliedTfsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAppliedTfSerializer

    def get_queryset(self):
        return TblAppliedTf.objects.all()

    def create(self, request, *args, **kwargs):
        print("In AppliedTfViewSet-Create")
        serializer = TblAppliedTfSerializer(data=request.data)
        if serializer.is_valid():
            applied_tf = serializer.save()
            return Response(data=TblAppliedGfSerializer(applied_tf,context={'request':request}).data,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class OnePerPagePagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size =1


class FullRightsUserHatTblUserIDundNameViewSet(UserHatTblUserIDundNameViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = OnePerPagePagination
    serializer_class = FullRightsUserHatTblUserIDundNameSerializer


class FullRightsTblAppliedRolleViewSet(TblAppliedRolleViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullRightsTblAppliedRolleSerializer


class FullRightsTblAppliedAfsViewSet(TblAppliedAfsViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullRightsTblAppliedAfSerializer


class FullRightsTblAppliedGfsViewSet(TblAppliedGfsViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullRightsTblAppliedGfSerializer


class FullRightsTblAppliedTfsViewSet(TblAppliedTfsViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullRightsTblAppliedTfSerializer


'''
class UserModelRightsViewSet(viewsets.ModelViewSet):
    
       # API endpoint that allows usermodelrights to be listed and detail-viewed
        #special listing with all rights expanded
    

    permission_classes = (IsAuthenticated,)
    serializer_class = UserModelRightsSerializer

    def get_queryset(self):
        return User.objects.all().order_by('name')


class CompleteUserListingViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be listed and detail-viewed
        special listing with all rights expanded
        filters request of search-view
        """
    permission_classes = (IsAuthenticated,)
    serializer_class = CompleteUserListingSerializer
    pagination_class = None

    def get_queryset(self):
        if 'search_what' in self.request.GET:
            search_what = self.request.GET["search_what"]
            user_search = self.request.GET["userSearch"]
            if search_what == "identity":
                users = User.objects.filter(identity__startswith=user_search).order_by('name')
            elif search_what == "name":
                users = User.objects.filter(name__startswith=user_search).order_by('name')
            elif search_what == "first_name":
                users = User.objects.filter(first_name__startswith=user_search).order_by('name')
            if 'orga' in self.request.GET:
                orga = self.request.GET['orga']
                users = users.filter(orga={'team': orga})

        else:
            return User.objects.all().order_by('name')
        return users


class UserListingViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows users to be listed and detail-viewed
        filters users after users-view API-Request
        """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserListingSerializer
    pagination_class = None

    def get_queryset(self):

        if 'search_what' in self.request.GET:
            search_what = self.request.GET["search_what"]
            user_search = self.request.GET["userSearch"]
            if search_what == "identity":
                users = User.objects.filter(identity__startswith=user_search).order_by('name')
            elif search_what == "name":
                users = User.objects.filter(name__startswith=user_search).order_by('name')
            elif search_what == "first_name":
                users = User.objects.filter(first_name__startswith=user_search).order_by('name')
            if 'orga' in self.request.GET:
                orga = self.request.GET['orga']
                users = users.filter(orga={'team': orga})
        else:
            return User.objects.all().order_by('name')
        return users


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.

    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    page_size = 10
    lookup_field = 'identity'

    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = UserFilter

    def get_queryset(self):
        return User.objects.all().order_by('name')


class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Roles to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.all()


class AFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AF's to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AFSerializer

    def get_queryset(self):
        return AF.objects.all()


class GFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows GF's to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = GFSerializer

    def get_queryset(self):
        return GF.objects.all()


class TFViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TF's to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TFSerializer
    pagination_class = None

    def get_queryset(self):
        return TF.objects.all()


class OrgaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orgas to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = OrgaSerializer
    pagination_class = None

    def get_queryset(self):
        return Orga.objects.all()


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.all()


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Departments to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        return Department.objects.all()


class ZI_OrganisationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ZI_Organisations to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ZI_OrganisationSerializer

    def get_queryset(self):
        return ZI_Organisation.objects.all()


class TF_ApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows TF_Applications to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = TF_ApplicationSerializer

    def get_queryset(self):
        return TF_Application.objects.all()


class ChangeRequestsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ChangeRequests to be viewed or edited.
    creates new changerequests after API-request from rightsapplication
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeRequestsSerializer
    pagination_class = None

    def get_queryset(self):
        return ChangeRequests.objects.all()

    def create(self, request, *args, **kwargs):
        print("In ViewSet-Create")
        data = request.data
        objects_to_change = json.loads(data['objects_to_change'])
        serializer = None
        added_requests = []
        for obj in objects_to_change:
            obj_data = {'requesting_user': data['requesting_user[value]'], 'compare_user': data['compare_user[value]'],
                        'action': obj[0]['value'], 'right_name': obj[1]['value'], 'right_type': obj[2]['value'],
                        'reason_for_action': obj[3]['value']}
            serializer = self.get_serializer(data=obj_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            added_requests.append(serializer.data['pk'])
        headers = self.get_success_headers(serializer.data)
        return Response(json.dumps(added_requests), status=status.HTTP_201_CREATED, headers=headers)
# Create your views here.
'''
