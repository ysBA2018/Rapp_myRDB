import csv
import json
import re

import requests
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import datetime
from MySQLdb import IntegrityError

from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse_lazy
from requests import ConnectionError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from .forms import CustomUserCreationForm, SomeForm, ApplyRightForm, DeleteRightForm, AcceptChangeForm, \
#   DeclineChangeForm, CustomAuthenticationForm, ProfileHeaderForm
from .models import *
from .forms import SomeForm, ApplyRightForm, DeleteRightForm, AcceptChangeForm, \
    DeclineChangeForm, CustomAuthenticationForm, ProfileHeaderForm, CustomUserCreationForm

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
docker_container_ip = "http://0.0.0.0:8000"
# docker_container_ip = "http://127.0.0.1:8000"


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

    def get_success_url(self):
        return reverse_lazy('myRDB:index')


class Logout(LogoutView):
    '''
        standard Logoutview uses django.auth includes CustomAuthentication-form
    '''
    template_name = 'myRDB/registration/logout.html'

    def get_next_page(self):
        return reverse_lazy('myRDB:index')


class Register(generic.CreateView):
    '''
        standard Register view uses  django.auth includes CustomUserCreationForm-form
        currently without email-verification
    '''
    # form_class = None
    form_class = CustomUserCreationForm
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
        self.extra_context['orgas'] = populate_orga_choice_field(headers, 'orgas', self.request)
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
        headers = get_headers(self.request)
        self.extra_context['orgas'] = populate_orga_choice_field(headers, 'orgas', self.request)
        # TODO: self.extra_context['roles'] = populate_role_choice_field(headers, 'roles', self.request)
        lis = ['zi_organisation', 'abteilung', 'gruppe']
        for e in lis:
            collection_title = e + 's'
            self.extra_context[collection_title] = populate_choice_fields(headers, e, self.request)
        url = docker_container_ip + '/api/useridundnamen/'
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


def populate_orga_choice_field(headers, field, request):
    '''
        method to populate selectboxes with data from REST-API
        used by search and users
    '''
    # url = 'http://' + request.get_host() + '/' + field + '/'
    url = docker_container_ip + '/api/' + field + '/'
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
    if 'abteilung' in request.GET:
        department = '----'
        if not request.GET['abteilung'] == '----':
            department = request.GET['abteilung']
            params = params + "&abteilung=" + department
        if extra_context.keys().__contains__("abteilung"):
            if department != extra_context["abteilung"]:
                changed = True
        else:
            changed = True
        extra_context["abteilung"] = department
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
    if 'gruppe' in request.GET:
        group = '----'
        if not request.GET['gruppe'] == '----':
            group = request.GET['gruppe']
            params = params + "&gruppe=" + group
        if extra_context.keys().__contains__("gruppe"):
            if group != extra_context["gruppe"]:
                changed = True
        else:
            changed = True
        extra_context["gruppe"] = group
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
        self.extra_context['current_host'] = docker_container_ip

        try:
            if 'user_search' in self.request.GET.keys():
                compareUserIdentity = self.request.GET['user_search']
            else:
                compareUserIdentity = self.request.session.get('user_search')

            self.request.session['user_search'] = compareUserIdentity

            headers = get_headers(self.request)
            legend_data_dict = create_legend(self.request, self.extra_context, headers)

            cached_af_descriptions = self.request.session.get('cached_af_descriptions')
            if not cached_af_descriptions:
                cached_af_descriptions = dict()

            user = get_user_by_name(compareUserIdentity, headers, self.request)[0]

            user_json_data = get_user_by_key(user['id'], headers=headers, request=self.request)

            compare_user_info = get_user_info_dict_for_all_applied_userids(headers, self.request, user_json_data)

            graph_data, scatterData, counts, cached_af_descriptions, data = prepareJSONdata(user, compare_user_info, True,
                                                                                      headers, self.request,
                                                                                      legend_data_dict,
                                                                                      cached_af_descriptions)
            self.request.session['cached_af_descriptions'] = cached_af_descriptions

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
            context["compareUser_table_data"] = data
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
            user_json_data = get_user_by_key(user['id'], headers, self.request)
            user_info = get_user_info_dict_for_all_applied_userids(headers, self.request, user_json_data)
            # roles = user_json_data['roles']

            legend_data_dict = create_legend(self.request, self.extra_context, headers)

            cached_af_descriptions = self.request.session.get('cached_af_descriptions')
            if not cached_af_descriptions:
                cached_af_descriptions = dict()

            try:
                graph_data, scatterData, counts, cached_af_descriptions, data = prepareJSONdata(user_json_data, user_info,
                                                                                          False, headers,
                                                                                          self.request,
                                                                                          legend_data_dict,
                                                                                          cached_af_descriptions)
                self.extra_context['jsondata'] = graph_data

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
                transfer_graph_data, transfer_list_with_category, transfer_rights_count, cached_af_descriptions, transfer_list_table_data = prepareTransferJSONdata(
                    user_info, self.request, headers, legend_data_dict, cached_af_descriptions)
                self.extra_context['transfer_list_count'] = transfer_rights_count

                self.extra_context['transferlist'] = transfer_graph_data
                self.extra_context['transfer_list_table_data'] = transfer_list_table_data
            except IOError:
                print("Error at compar - creating transfer_graph")

            try:
                delete_graph_data, delete_list_with_category, delete_rights_count, cached_af_descriptions,delete_list_table_data = prepareDeleteJSONdata(
                    user_info, self.request, headers, legend_data_dict, cached_af_descriptions)
                self.extra_context['delete_list_table_data'] = delete_list_table_data
                self.extra_context['delete_list_count'] = delete_rights_count
                self.extra_context['deletelist'] = delete_graph_data
            except IOError:
                print("Error at compar - creating delete_graph")

            self.request.session['cached_af_descriptions'] = cached_af_descriptions

            return data
        except IOError:
            print("Error at Compare - comparingUser")
        return data


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
        self.extra_context['current_host'] = docker_container_ip
        setViewMode(self.request, self.extra_context)
        headers = get_headers(self.request)

        legend_data_dict = create_legend(self.request, self.extra_context, headers)

        cached_af_descriptions = self.request.session.get('cached_af_descriptions')


        user_pk = self.request.session.get('user_pk')
        user_json_data = get_user_by_key(user_pk, headers, self.request)
        user_info = get_user_info_dict_for_all_applied_userids(headers, self.request, user_json_data)
        self.extra_context['user_userid_combi_id'] = user_info[0]['rights_data']['id']

        graph_data, scatterData, counts, cached_af_descriptions, table_data = prepareJSONdata(self.request.session['user_identity'], user_info, False, headers,
                                                                                  self.request, legend_data_dict,
                                                                                  cached_af_descriptions)


        transfer_graph_data, transfer_list_with_category, transfer_rights_count, cached_af_descriptions, transfer_table_data = prepareTransferJSONdata(
            user_info,
            self.request,
            headers,
            legend_data_dict,
            cached_af_descriptions)
        self.extra_context['transfer_list_table_data'] = transfer_table_data

        delete_graph_data, delete_list_with_category, delete_rights_count, cached_af_descriptions, delete_table_data = prepareDeleteJSONdata(
            user_info,
            self.request, headers,
            legend_data_dict,
            cached_af_descriptions)

        self.extra_context['delete_list_table_data'] = delete_table_data

        self.extra_context['transfer_list_count'] = transfer_rights_count
        self.extra_context['delete_list_count'] = delete_rights_count
        self.extra_context['deletelist'] = delete_graph_data
        self.extra_context['transferlist'] = transfer_graph_data

        self.extra_context['delete_list_table_data'] = delete_table_data
        self.extra_context['transfer_list_table_data'] = transfer_table_data

        if self.request.GET.keys().__contains__("level"):
            self.extra_context['level'] = self.request.GET['level']
        else:
            self.extra_context['level'] = 'ROLLE'

        equalRights = []
        unequalRights = []
        equalModelRights = []
        unequalModelRights = []
        equalRightsStats = []
        unequalRightsStats = []

        equalModelRights, equalRights, equalRightsStats, unequalModelRights, unequalRights, unequalRightsStats = self.compare_right_and_modelright(
            equalModelRights, equalRights, equalRightsStats, headers, unequalModelRights, unequalRights,
            unequalRightsStats, graph_data, legend_data_dict, cached_af_descriptions)

        self.extra_context['equal_rights'] = sorted(equalRights, key=lambda k: k['name'])
        self.extra_context['unequal_rights'] = sorted(unequalRights, key=lambda k: k['name'])
        self.extra_context['equal_model_rights'] = sorted(equalModelRights, key=lambda k: k['name'])
        self.extra_context['unequal_model_rights'] = sorted(unequalModelRights, key=lambda k: k['name'])
        self.extra_context['equal_rights_stats'] = sorted(equalRightsStats, key=lambda k: k['right_name'])
        self.extra_context['unequal_rights_stats'] = sorted(unequalRightsStats, key=lambda k: k['right_name'])

        self.extra_context['user_identity'] = self.request.session.get('user_identity')
        self.extra_context['user_first_name'] = self.request.session.get('user_first_name')
        self.extra_context['user_name'] = self.request.session.get('user_name')
        self.extra_context['user_department'] = self.request.session.get('user_department')

        self.extra_context['user_count'] = self.request.session.get('user_count')
        self.extra_context['role_count'] = self.request.session.get('role_count')
        self.extra_context['af_count'] = self.request.session.get('af_count')
        self.extra_context['gf_count'] = self.request.session.get('gf_count')
        self.extra_context['tf_count'] = self.request.session.get('tf_count')
        return None

    def compare_right_and_modelright(self, equalModelRights, equalRights, equalRightsStats, headers, unequalModelRights,
                                     unequalRights, unequalRightsStats, user_data, legend_data_dict,
                                     cached_af_descriptions):
        for user in user_data['children']:
            if self.extra_context['level'] == "ROLLE":
                rollen = sorted(user['children'], key=lambda k: k['name'])
                for rolle in rollen:
                    full_model_rolle_id_url = rolle['model_rolle_id']['url'].replace('rolle', 'fullrolle')
                    current_model = get_by_url(full_model_rolle_id_url, headers)
                    stats = {}
                    stats['right_name'] = current_model['rollenname']
                    stats['description'] = current_model['rollenbeschreibung']
                    stats['model_af_count'], stats['model_gf_count'], stats[
                        'model_tf_count'] = self.prepareModelJSONdata(current_model, True, False, False,
                                                                      headers, legend_data_dict, None)
                    equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats = self.compareRightToModel(
                        rolle,
                        current_model,
                        equalRights,
                        unequalRights,
                        equalModelRights,
                        unequalModelRights,
                        True,
                        False,
                        False,
                        stats,
                        unequalRightsStats,
                        equalRightsStats)

            elif self.extra_context['level'] == "AF":
                rollen = sorted(user['children'], key=lambda k: k['name'])
                for rolle in rollen:
                    afs = sorted(rolle['children'], key=lambda k: k['name'])
                    for af in afs:
                        full_model_af_id_url = af['model_af_id']['url'].replace('af', 'fullaf')
                        current_model = get_by_url(full_model_af_id_url, headers)
                        stats = {}
                        stats['right_name'] = current_model['af_name']
                        stats['model_af_count'], stats['model_gf_count'], stats[
                            'model_tf_count'] = self.prepareModelJSONdata(current_model, False, True, False,
                                                                          headers, legend_data_dict,
                                                                          cached_af_descriptions)
                        stats['description'] = current_model['af_beschreibung']

                        equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats = self.compareRightToModel(
                            af,
                            current_model,
                            equalRights,
                            unequalRights,
                            equalModelRights,
                            unequalModelRights,
                            False,
                            True,
                            False,
                            stats,
                            unequalRightsStats,
                            equalRightsStats)

            elif self.extra_context['level'] == "GF":
                rollen = sorted(user['children'], key=lambda k: k['name'])
                for rolle in rollen:
                    afs = sorted(rolle['children'], key=lambda k: k['name'])
                    for af in afs:
                        gfs = sorted(af['children'], key=lambda k: k['name'])
                        for gf in gfs:
                            full_model_gf_id_url = gf['model_gf_id']['url'].replace('afgfs', 'fullafgfs')
                            current_model = get_by_url(full_model_gf_id_url, headers)
                            stats = {}
                            stats['right_name'] = current_model['name_gf_neu']
                            stats['model_af_count'], stats['model_gf_count'], stats[
                                'model_tf_count'] = self.prepareModelJSONdata(current_model, False, False, True,
                                                                              headers, legend_data_dict, None)
                            stats['description'] = current_model['gf_beschreibung']

                            equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats = self.compareRightToModel(
                                gf,
                                current_model,
                                equalRights,
                                unequalRights,
                                equalModelRights,
                                unequalModelRights,
                                False,
                                False,
                                True,
                                stats,
                                unequalRightsStats,
                                equalRightsStats)
        return equalModelRights, equalRights, equalRightsStats, unequalModelRights, unequalRights, unequalRightsStats

    def compareRightToModel(self, userRight, compareModel, equalRights, unequalRights, equalModelRights,
                            unequalModelRights, isRolle, isAF, isGF, stats, unequalRightsStats, equalRightsStats):
        equal = False
        equalAFSum = 0
        equalGFSum = 0
        equalTFSum = 0

        tf_count = 0
        tf_count_diff = 0
        gf_count = 0
        gf_count_diff = 0

        if isRolle:
            af_count = len(userRight['children'])
            af_count_diff = stats['model_af_count'] - af_count

            stats['af_count'] = af_count
            stats['af_count_diff'] = af_count_diff

            for af in sorted(userRight['children'], key=lambda k: k['name']):
                through = False
                modelAFIter = iter(sorted(compareModel['children'], key=lambda k: k['name']))

                while not through:
                    try:
                        currentAFModel = next(modelAFIter)
                        if af['name'] == currentAFModel['name']:
                            equalAFSum += 1
                            break
                    except StopIteration:
                        print('Model_AF stop iteration')
                        through = True
                        return equalRights, unequalRights, equalModelRights, unequalModelRights, equalRightsStats, unequalRightsStats
                if af['children']:
                    gf_count += len(af['children'])
                for gf in sorted(af['children'], key=lambda k: k['name']):
                    through = False
                    modelGFIter = iter(sorted(currentAFModel['children'], key=lambda k: k['name']))
                    while not through:
                        try:
                            currentGFModel = next(modelGFIter)
                            if gf['name'] == currentGFModel['name']:
                                equalGFSum += 1
                                break
                        except StopIteration:
                            print('Model_GF stop iteration')
                            through = True

                    tf_count += len(gf['children'])

                    for tf in sorted(gf['children'], key=lambda k: k['name']):
                        modelTFIter = iter(sorted(currentGFModel['children'], key=lambda k: k['name']))
                        through = False
                        while not through:
                            try:
                                currentTFModel = next(modelTFIter)
                                if tf['name'] == currentTFModel['name']:
                                    equalTFSum += 1
                                    break
                            except StopIteration:
                                print('Model_GF stop iteration')
                                through = True
            if equalAFSum == stats['model_af_count'] and equalGFSum == stats['model_gf_count'] and equalTFSum == stats[
                'model_tf_count'] and af_count_diff == 0 and gf_count_diff == 0 and tf_count_diff == 0:
                equal = True
        if isAF:
            for gf in sorted(userRight['children'], key=lambda k: k['name']):
                through = False
                modelGFIter = iter(sorted(compareModel['children'], key=lambda k: k['name']))
                if userRight['children']:
                    gf_count += len(userRight['children'])
                while not through:
                    try:
                        currentGFModel = next(modelGFIter)
                        if gf['name'] == currentGFModel['name']:
                            equalGFSum += 1
                            break
                    except StopIteration:
                        print('Model_GF stop iteration')
                        through = True

                tf_count += len(gf['children'])

                for tf in sorted(gf['children'], key=lambda k: k['name']):
                    modelTFIter = iter(sorted(currentGFModel['children'], key=lambda k: k['name']))
                    through = False
                    while not through:
                        try:
                            currentTFModel = next(modelTFIter)
                            if tf['name'] == currentTFModel['name']:
                                equalTFSum += 1
                                break
                        except StopIteration:
                            print('Model_TF stop iteration')
                            through = True
            if equalGFSum == stats['model_gf_count'] and equalTFSum == stats[
                'model_tf_count'] and gf_count_diff == 0 and tf_count_diff == 0:
                equal = True
        if isGF:
            tf_count = len(userRight['children'])
            for tf in sorted(userRight['children'], key=lambda k: k['name']):
                through = False
                modelTFIter = iter(sorted(compareModel['children'], key=lambda k: k['name']))

                while not through:
                    try:
                        currentTFModel = next(modelTFIter)
                        if tf['name'] == currentTFModel['name']:
                            equalTFSum += 1
                            break
                    except StopIteration:
                        print('Model_TF stop iteration')
                        through = True
            if equalTFSum == stats['model_tf_count'] and tf_count_diff == 0:
                equal = True

        gf_count_diff = stats['model_gf_count'] - gf_count
        stats['gf_count'] = gf_count
        stats['gf_count_diff'] = gf_count_diff

        tf_count_diff = stats['model_tf_count'] - tf_count
        stats['tf_count'] = tf_count
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

    def prepareModelJSONdata(self, json_data, is_rolle, is_af, is_gf, headers, legend_data, cached_af_descriptions):
        model_af_count = 0
        model_gf_count = 0
        model_tf_count = 0
        if is_rolle:
            af_old = None
            json_data["name"] = json_data.pop('rollenname')
            json_data["children"] = json_data['afs']
            for model_af in json_data['children']:
                model_af["name"] = model_af['af_name']
                model_af["children"] = model_af['gfs']
                for model_gf in model_af['children']:
                    model_gf["name"] = model_gf['name_gf_neu']
                    model_gf["children"] = model_gf['tfs']
                    if model_gf['children']:
                        if model_af != af_old:
                            model_af_count += 1
                            af_old = model_af
                        model_gf_count += 1
                        model_tf_count += len(model_gf['children'])

                    for model_tf in model_gf['children']:
                        if model_tf['tf_schreibweise']:
                            model_tf['name'] = model_tf['tf_schreibweise'][0]['schreibweise']
                        else:
                            model_tf["name"] = model_tf['tf']
                        plattform = model_tf['plattform']
                        hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                        model_tf['color'] = hslColor
                        model_tf["size"] = 2000
        elif is_af:
            json_data["name"] = json_data['af_name']
            af_beschreibung = cached_af_descriptions.get(json_data['af_name'])
            if af_beschreibung:
                json_data['af_beschreibung'] = af_beschreibung[0]['af_beschreibung']
            else:
                json_data['af_beschreibung'] = "Keine Beschreibung vorhanden!"
            json_data["children"] = json_data['gfs']
            for model_gf in json_data['children']:
                model_gf["name"] = model_gf['name_gf_neu']
                model_gf["children"] = model_gf['tfs']
                if model_gf['children']:
                    model_gf_count += 1
                    model_tf_count += len(model_gf['children'])

                for model_tf in model_gf['children']:
                    if model_tf['tf_schreibweise']:
                        model_tf['name'] = model_tf['tf_schreibweise'][0]['schreibweise']
                    else:
                        model_tf["name"] = model_tf['tf']
                    plattform = model_tf['plattform']
                    hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                    model_tf['color'] = hslColor
                    model_tf["size"] = 2000
        elif is_gf:
            json_data["name"] = json_data['name_gf_neu']
            json_data['gf_beschreibung'] = None
            json_data["children"] = json_data['tfs']
            if json_data['tfs']:
                model_tf_count += len(json_data['children'])

            for model_tf in json_data['children']:
                if model_tf['tf_schreibweise']:
                    model_tf['name'] = model_tf['tf_schreibweise'][0]['schreibweise']
                else:
                    model_tf["name"] = model_tf['tf']
                if not json_data['gf_beschreibung']:
                    if 'gf_beschreibung' in model_tf:
                        json_data['gf_beschreibung'] = model_tf['gf_beschreibung']
                    else:
                        json_data['gf_beschreibung'] = "Keine Beschreibung vorhanden!"
                plattform = model_tf['plattform']
                hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                model_tf['color'] = hslColor
                model_tf["size"] = 2000
        return model_af_count, model_gf_count, model_tf_count


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

        legend_data_dict = create_legend(self.request, self.extra_context, headers)

        cached_af_descriptions = self.request.session.get('cached_af_descriptions')
        if not cached_af_descriptions:
            cached_af_descriptions = dict()

        try:
            self.extra_context['no_profile'] = None
            user_pk = user.pk
        except UnboundLocalError:
            userid_und_name = get_useridundnamen_by_userid(user_id.upper(), headers)[0]
            user_hat_user_id_und_name = get_user_userid_name_combination(headers, None, userid_und_name['id'],
                                                                         self.request)
            if user_hat_user_id_und_name:
                user_hat_user_id_und_name = user_hat_user_id_und_name[0]
                user_json = get_by_url(user_hat_user_id_und_name['user_name'], headers)
                user_pk = user_json['id']
                user = User.objects.get(id=user_pk)
            else:
                self.extra_context.clear()
                self.extra_context[
                    'no_profile'] = "Diese NutzerID-Name-Kombination wurde noch keinem Nutzer zugewiesen.\n" \
                                    "Bitte erzeugen Sie für " + user_id + " per Admin ein Nutzerprofil\n" \
                                                                          "oder weisen Sie diese einem Nutzer zu!"
                return

        self.request.session['user_pk']=user_pk
        user_json_data = get_user_by_key(user_pk, headers, self.request)
        user_info = get_user_info_dict_for_all_applied_userids(headers, self.request, user_json_data)

        last_import = get_last_import(headers)[0]['end']
        last_import_datetime = datetime.datetime.strptime(last_import, '%Y-%m-%dT%H:%M:%S.%fZ')
        last_rights_update = user.last_rights_update

        if last_rights_update is None or last_import_datetime > last_rights_update.replace(tzinfo=None):
            for ui in user_info:
                clear_personal_rights_models(ui,headers, self.request)
                update_personal_right_models(ui, headers, self.request)

            last_rights_update = datetime.datetime.now()
            patch_user_last_rights_update(user_pk, last_rights_update, headers)
            user_info = get_user_info_dict_for_all_applied_userids(headers, self.request, user_json_data)

        graph_data, scatterData, counts, cached_af_descriptions, table_data = prepareJSONdata(user_id, user_info, False, headers,
                                                                                  self.request, legend_data_dict,
                                                                                  cached_af_descriptions)

        self.extra_context['scatterData'] = scatterData

        transfer_graph_data, transfer_list_with_category, transfer_rights_count, cached_af_descriptions, transfer_table_data = prepareTransferJSONdata(
            user_info,
            self.request,
            headers,
            legend_data_dict,
            cached_af_descriptions)
        self.extra_context['transferlist'] = transfer_graph_data
        self.extra_context['transfer_list_table_data'] = transfer_table_data
        self.extra_context['transfer_list_count'] = transfer_rights_count

        delete_graph_data, delete_list_with_category, delete_rights_count, cached_af_descriptions, delete_table_data = prepareDeleteJSONdata(
            user_info,
            self.request, headers,
            legend_data_dict,
            cached_af_descriptions)
        self.request.session['cached_af_descriptions'] = cached_af_descriptions
        # delete_list, delete_list_with_category = [],[]
        self.extra_context['deletelist'] = delete_graph_data
        self.extra_context['delete_list_table_data'] = delete_table_data
        self.extra_context['delete_list_count'] = delete_rights_count

        # afs = user_json_data['children']
        # data, gf_count, tf_count = prepareTableData(user_json_data, roles, afs, headers)

        self.request.session['user_data'] = graph_data
        self.extra_context['jsondata'] = self.request.session.get('user_data')

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

        self.extra_context['user_id'] = user.pk
        self.extra_context['user_identity'] = user.username
        self.request.session['user_identity'] = user.username
        self.extra_context['user_first_name'] = user.first_name
        self.request.session['user_first_name'] = user.first_name
        self.extra_context['user_name'] = user.last_name
        self.request.session['user_name'] = user.last_name

        if graph_data['children']:
            self.extra_context['user_department'] = graph_data['children'][0]['gruppe']
            self.request.session['user_department'] = graph_data['children'][0]['gruppe']
        else:
            self.extra_context['user_department'] = "Kein Nutzer & daher keine Gruppe zugewiesen!"
            self.request.session['user_department'] = "Kein Nutzer & daher keine Gruppe zugewiesen!"

        self.request.session['user_count'] = counts['user']
        self.request.session['role_count'] = counts['roles']
        self.request.session['af_count'] = counts['afs']
        self.request.session['gf_count'] = counts['gfs']
        self.request.session['tf_count'] = counts['tfs']

        return table_data
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
        headers = get_headers(self.request)
        self.extra_context['current_host'] = docker_container_ip

        legend_data_dict = create_legend(self.request, self.extra_context, headers)

        change_requests_json_data = get_changerequests(get_headers(self.request), self.request)
        print(change_requests_json_data)
        requests_by_users = self.repack_data(change_requests_json_data, headers, legend_data_dict)
        print(requests_by_users)
        self.extra_context['requesting_users'] = requests_by_users
        self.extra_context['accept_form'] = AcceptChangeForm
        self.extra_context['decline_form'] = DeclineChangeForm
        return []

    def repack_data(self, change_requests, headers, legend_data_dict):
        list_by_user = []
        for data in change_requests:
            if data['status'] == "unanswered":
                user_dict = {'requesting_user': data['requesting_user'], 'apply_requests': [], 'delete_requests': []}
                if not list_by_user.__contains__(user_dict):
                    list_by_user.append(user_dict)
        cached_user_data = dict()
        for data in change_requests:
            for user in list_by_user:
                if user['requesting_user'] == data['requesting_user']:
                    if not data['requesting_user'] in cached_user_data:
                        requesting_user_json = get_user_by_name(user['requesting_user'].lower(), headers, self.request)[
                            0]
                        requesting_user_info = get_user_info_dict_for_all_applied_userids(headers, self.request,
                                                                                          requesting_user_json)
                        requesting_user = requesting_user_info[0]['rights_data']
                        cached_user_data[data['requesting_user']] = requesting_user_info[0]['rights_data']
                    else:
                        requesting_user = cached_user_data.get(data['requesting_user'])
                    if data['status'] == "unanswered":
                        # TODO: xv-nummer als SLUG-Field -> dann url über xvnummer aufrufbar
                        if data['action'] == 'apply':
                            right = get_right_from_list(requesting_user, data['right_type'], data['right_name'],
                                                        requesting_user['transfer_list'], headers, legend_data_dict)
                            if right is None:
                                model = None
                            else:
                                model = right['model_right_pk']
                            user["apply_requests"].append({'right': right, 'model': model, 'type': data['right_type'],
                                                           'right_name': data['right_name'],
                                                           'reason_for_action': data['reason_for_action'],
                                                           'request_pk': data['pk']})
                        else:
                            right = get_right_from_list(requesting_user, data['right_type'], data['right_name'],
                                                        requesting_user['delete_list'], headers, legend_data_dict)
                            if right is None:
                                model = None
                            else:
                                model = right['model_right_pk']

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
        self.extra_context['current_host'] = docker_container_ip
        if 'user_identity' in self.request.session:
            user_identity = self.request.session.get('user_identity')
        else:
            user_identity = self.request.user.username
        self.extra_context['requesting_user'] = user_identity
        # setViewMode(self.request, self.extra_context)
        headers = get_headers(self.request)

        legend_data_dict = create_legend(self.request, self.extra_context, headers)

        user = get_user_by_name(user_identity.lower(), headers, self.request)[0]
        user_info = get_user_info_dict_for_all_applied_userids(headers, self.request, user)
        self.extra_context['requesting_user_userid_combination_pk'] = user_info[0]['rights_data']['id']

        request_list = self.get_my_requests(user_info[0]['rights_data'])
        repacked_request_list = self.repack_list(request_list, user_info, headers, legend_data_dict)
        unanswered_list, accepted_list, declined_list = self.presort(repacked_request_list)
        self.extra_context['declined_list'] = declined_list
        self.extra_context['unanswered_list'] = unanswered_list
        return accepted_list

    def repack_list(self, list, user_info, headers, legend_data_dict):
        repacked_list = []
        requesting_user = user_info[0]['rights_data']
        for request in list:
            if request['action'] == 'apply':
                # TODO: wenn berechtigung auf comp_user oder user seite gelöscht wurde -> zuerst modell-recht anzeigen -> wenn auch gelöscht - dann erst None setzen und damit esatz-circle anzeigen
                if request['status'] == "accepted":
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['rollen'], headers, legend_data_dict)
                    if right is None:
                        model = None
                    else:
                        model = right['model_right_pk']

                elif request['status'] == "declined":
                    compare_user_json = get_user_by_name(request['compare_user'], headers, self.request)[0]
                    compare_user_info = get_user_info_dict_for_all_applied_userids(headers, self.request,
                                                                                   compare_user_json)
                    compare_user = compare_user_info[0]['rights_data']
                    right = get_right_from_list(compare_user, request['right_type'], request['right_name'],
                                                compare_user['rollen'], headers, legend_data_dict)
                    if right is None:
                        model = None
                    else:
                        model = right['model_right_pk']
                else:
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['transfer_list'], headers, legend_data_dict)
                    if right is None:
                        model = None
                    else:
                        model = right['model_right_pk']
            if request['action'] == 'delete':
                if request['status'] == "accepted":
                    right = None
                    model = None
                elif request['status'] == "declined":
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['rollen'], headers, legend_data_dict)
                    if right is None:
                        model = None
                    else:
                        model = right['model_right_pk']
                else:
                    right = get_right_from_list(requesting_user, request['right_type'], request['right_name'],
                                                requesting_user['delete_list'], headers, legend_data_dict)
                    if right is None:
                        model = None
                    else:
                        model = right['model_right_pk']

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
        self.extra_context['current_host'] = docker_container_ip
        self.extra_context['current_site'] = "right_application"
        self.extra_context['compare_user'] = self.request.session.get('user_search')
        user_identity = self.request.session.get('user_identity')
        self.extra_context['requesting_user'] = user_identity
        # setViewMode(self.request, self.extra_context)
        headers = get_headers(self.request)

        legend_data_dict = create_legend(self.request, self.extra_context, headers)

        cached_af_descriptions = self.request.session.get('cached_af_descriptions')
        if not cached_af_descriptions:
            cached_af_descriptions = dict()

        user_json_data = get_user_by_name(user_identity, headers, self.request)[0]
        user_info = get_user_info_dict_for_all_applied_userids(headers, self.request, user_json_data)
        self.extra_context['requesting_user_userid_combination_pk'] = user_info[0]['rights_data']['id']

        graph_data, scatterData, counts, cached_af_descriptions, table_data = prepareJSONdata(user_json_data['username'], user_info,
                                                                                  False, headers,
                                                                                  self.request, legend_data_dict,
                                                                                  cached_af_descriptions)

        transfer_graph_data, transfer_list_with_category, single_rights_count, cached_af_descriptions, transfer_list_table_data = prepareTransferJSONdata(
            user_info, self.request, headers, legend_data_dict, cached_af_descriptions)
        model_transfer_list = get_model_list(transfer_list_with_category, cached_af_descriptions, headers)
        self.extra_context['transfer_list_table_data'] = transfer_list_table_data
        # self.extra_context['transfer_list_count'] = transfer_list_count
        self.extra_context['transfer_list'] = transfer_graph_data
        self.extra_context['stripped_transfer_list'] = [right['right'] for right in transfer_list_with_category]

        self.extra_context['model_transfer_list'] = model_transfer_list
        self.extra_context['transfer_form'] = ApplyRightForm

        delete_graph_data, delete_list_with_category, single_rights_count, cached_af_descriptions,delete_list_table_data = prepareDeleteJSONdata(
            user_info, self.request, headers, legend_data_dict, cached_af_descriptions)
        model_delete_list = get_model_list(delete_list_with_category, cached_af_descriptions, headers)
        self.extra_context['delete_list_table_data'] = delete_list_table_data
        # self.extra_context['delete_list_count'] = delete_list_count

        self.extra_context['delete_list'] = delete_graph_data
        self.extra_context['stripped_delete_list'] = [right['right'] for right in delete_list_with_category]

        self.extra_context['model_delete_list'] = model_delete_list
        self.extra_context['delete_form'] = DeleteRightForm

        self.extra_context['jsondata'] = user_json_data

        # afs = user_json_data['children']
        # data, gf_count, tf_count = prepareTableData(user, roles, afs, headers)

        self.extra_context['user_identity'] = user_json_data['username']
        self.extra_context['user_first_name'] = user_json_data['first_name']
        self.extra_context['user_name'] = user_json_data['last_name']
        if graph_data['children']:
            self.extra_context['user_department'] = graph_data['children'][0]['gruppe']
        else:
            self.extra_context['user_department'] = "Kein Nutzer & daher keine Gruppe zugewiesen!"

        self.extra_context['user_count'] = self.request.session.get('user_count')
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


def get_right_from_list(comp_user, type, right, rights, headers, legend_data):
    '''
        method used by my_requests and request_pool for finding specific right in a list and
        preparing right_data for display as circlePacking
    :param comp_user:
    :param type:
    :param right:
    :param rights:
    :return:
    '''
    for rolle in rights:
        if type == 'ROLLE':
            if rolle['model_rolle_id']['rollenname'] == right:
                rolle['name'] = rolle['model_rolle_id']['rollenname']
                rolle['children'] = rolle['applied_afs']
                rolle['model_right_pk'] = rolle['model_rolle_id']
                for af in rolle['children']:
                    af['name'] = af['model_af_id']['af_name']
                    af['children'] = af['applied_gfs']
                    for gf in af['children']:
                        gf['name'] = gf['model_gf_id']['name_gf_neu']
                        gf['children'] = gf['applied_tfs']
                        for tf in gf['children']:
                            model_tf = tf['model_tf_id']
                            if model_tf['tf_schreibweise']:
                                tf['name'] = model_tf['tf_schreibweise'][0]['schreibweise']
                            else:
                                tf["name"] = model_tf['tf']
                            plattform = model_tf['plattform']
                            hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                            tf['color'] = hslColor
                            tf['size'] = 2000
                return rolle
        elif type == 'AF':
            for af in rolle['applied_afs']:
                if af['model_af_id']['af_name'] == right:
                    af['name'] = af['model_af_id']['af_name']
                    af['children'] = af['applied_gfs']
                    af['model_right_pk'] = af['model_af_id']
                    for gf in af['children']:
                        gf['name'] = gf['model_gf_id']['name_gf_neu']
                        gf['children'] = gf['applied_tfs']
                        for tf in gf['children']:
                            model_tf = tf['model_tf_id']
                            if model_tf['tf_schreibweise']:
                                tf['name'] = model_tf['tf_schreibweise'][0]['schreibweise']
                            else:
                                tf["name"] = model_tf['tf']
                            plattform = model_tf['plattform']
                            hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                            tf['color'] = hslColor
                            tf['size'] = 2000
                    return af
        elif type == 'GF':
            for af in rolle['applied_afs']:
                for gf in af['applied_gfs']:
                    if gf['model_gf_id']['name_gf_neu'] == right:
                        gf['model_right_pk'] = gf['model_gf_id']
                        gf['name'] = gf['model_gf_id']['name_gf_neu']
                        gf['children'] = gf['applied_tfs']
                        for tf in gf['children']:
                            model_tf = tf['model_tf_id']
                            if model_tf['tf_schreibweise']:
                                tf['name'] = model_tf['tf_schreibweise'][0]['schreibweise']
                            else:
                                tf["name"] = model_tf['tf']
                            plattform = model_tf['plattform']
                            hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                            tf['color'] = hslColor
                            tf['size'] = 2000
                        return gf
        elif type == 'TF':
            for af in rolle['applied_afs']:
                for gf in af['applied_gfs']:
                    for tf in gf['applied_tfs']:
                        if tf['model_tf_id']['tf'] == right:
                            model_tf = tf['model_tf_id']
                            if model_tf['tf_schreibweise']:
                                tf['name'] = model_tf['tf_schreibweise'][0]['schreibweise']
                            else:
                                tf["name"] = model_tf['tf']
                            plattform = model_tf['plattform']
                            hslColor = "hsl(%d, 50%%, 50%%)" % int(plattform['color'])
                            tf['color'] = hslColor
                            tf['size'] = 2000
                            tf['model_right_pk'] = tf['model_tf_id']
                            return tf


def get_model_list(transfer_list_with_category, cached_af_descriptions, headers):
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
        if right['type'] == 'rolle':
            model = right['right']['model_rolle_id']
            model['right_name'] = model['rollenname']
            model['description'] = model['rollenbeschreibung']
        elif right['type'] == 'af':
            model = right['right']['model_af_id']
            model['right_name'] = model.pop('af_name')
            if model['id'] in cached_af_descriptions:
                model['description'] = cached_af_descriptions.get(model['id'])
            else:
                model['description'] = "Keine beschreibung voranden!"

        elif right['type'] == 'gf':
            model = right['right']['model_gf_id']
            model['right_name'] = model.pop('name_gf_neu')
            first_tf = get_by_url(model['tfs'][0], headers)
            if 'gf_beschreibung' in first_tf:
                model['description'] = first_tf['gf_beschreibung']
            else:
                model['description'] = "Keine beschreibung voranden!"


        elif right['type'] == 'tf':
            model = right['right']['model_tf_id']
            model['right_name'] = model.pop('tf')
            model['description'] = model.pop('tf_beschreibung')
        model['type'] = right['type'].upper()
        model_list.append(model)
    return model_list


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


def populate_choice_fields(headers, e, request):
    url = docker_container_ip + '/api/useridundnamen/?field=' + e
    json_data = get_by_url(url, headers)
    if type(json_data) == list:
        results = {e: json_data}
    if type(json_data) == dict:
        results = {e: json_data['results']}
    response = Response(results)
    return response.data[e]


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


def create_legend(request, extra_context, headers):
    legend_data_dict = request.session.get('legend_data_dict')
    legend_data = request.session.get('legend_data')
    if (not legend_data_dict or not legend_data):
        legend_data = get_tf_applications(headers, request)
        sorted_legend_data = sorted(legend_data, key=lambda r: r["tf_technische_plattform"])
        extra_context['legendData'] = sorted_legend_data
        legend_data_dict = {x['url']: x for x in legend_data}
        request.session['legend_data_dict'] = legend_data_dict
        request.session['legend_data'] = legend_data
    elif (legend_data_dict and legend_data) and not 'legendData' in extra_context:
        sorted_legend_data = sorted(legend_data, key=lambda r: r["tf_technische_plattform"])
        extra_context['legendData'] = sorted_legend_data

    return legend_data_dict


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


def get_af_by_name(af_name, headers, request):
    '''
        Get-Method for API-Requests
        gets specific AF by key
    :param headers:
    :param request:
    :return:
    '''
    # url = 'http://' + request.get_host() + '/afs/%d' % pk
    af_name = af_name.replace('#', '%23')
    url = docker_container_ip + '/api/afs/?af_name=%s' % af_name
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


def get_gf_by_name(gf_name, headers, request):
    '''
            Get-Method for API-Requests
            gets specific GF by key
        :param headers:
        :param request:
        :return:
        '''
    # url = 'http://' + request.get_host() + '/gfs/%d' % pk
    gf_name = gf_name.replace('#', '%23')
    url = docker_container_ip + '/api/afgfs/?gf_name=%s' % gf_name
    gf_json = requests.get(url, headers=headers).json()
    if 'results' in gf_json:
        gf_json = gf_json['results']
    elif 'detail' in gf_json:
        print(gf_json['detail'])
        raise ConnectionError(gf_json['detail'])
    return gf_json


def get_gf_by_name_and_af_name(gf_name, af_name, headers, request):
    '''
            Get-Method for API-Requests
            gets specific GF by key
        :param headers:
        :param request:
        :return:
        '''
    # url = 'http://' + request.get_host() + '/gfs/%d' % pk
    gf_name = gf_name.replace('#', '%23')
    af_name = af_name.replace('#', '%23')
    url = docker_container_ip + '/api/afgfs/?gf_name=' + gf_name + '&af_name=' + af_name
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


def get_useridundnamen_by_userid(user_id, headers):
    url = docker_container_ip + '/api/useridundnamen/?xvnumber=%s' % user_id
    res = requests.get(url, headers=headers)
    json = res.json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_rolle_by_rollenname(rollenname, headers, request):
    '''
        Get-Method for API-Requests
        gets specific User by xvNumber as key
    :param headers:
    :param request:
    :return:
    '''
    # url = 'http://' + request.get_host() + '/users/%s' % pk
    url = docker_container_ip + '/api/rollen/?rollenname=%s' % rollenname
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
    url = docker_container_ip + '/api/changerequests/'
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
    url = docker_container_ip + '/api/userhatrollen/?user_id=' + str(user_pk)
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_user_hat_rolle_by_ids(user_id, rollenname, headers):
    url = docker_container_ip + '/api/userhatrollen/?user_id=' + str(user_id) + '&rollenname=' + str(rollenname)
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_rolle_hat_af_by_ids(rollenname, af_id, headers):
    url = docker_container_ip + '/api/rollehatafs/?rollenname=' + str(rollenname) + '&af_id=' + str(af_id)
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_af_hat_gf_by_ids(af_id, gf_id, headers):
    url = docker_container_ip + '/api/afhatgfs/?af_id=' + str(af_id) + '&gf_id=' + str(gf_id)
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_gf_hat_tf_by_ids(gf_id, tf_id, headers):
    url = docker_container_ip + '/api/gfhattfs/?gf_id=' + str(gf_id) + '&tf_id=' + str(tf_id)
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_tf_hat_schreibweise_by_ids(tf_id, schreibweise_id, headers):
    url = docker_container_ip + '/api/tfhatschreibweisen/?tf_id=' + str(tf_id) + '&schreibweise_id=' + str(schreibweise_id)
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
    url = docker_container_ip + '/api/userhatuseridundnamen/?user_pk=' + str(user_pk) + '&userid_name_pk=' + str(
        userid_name_pk)
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
    url = docker_container_ip + '/api/fulluserhatuseridundnamen/?user_pk=' + str(user_pk) + '&userid_name_pk=' + str(
        userid_name_pk)
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
    af_name = af_name.replace('#', '%23')
    url = docker_container_ip + '/api/afgfs/?af_name=' + af_name
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_AppliedRolle_by_rollenid(rollenid, user_id_name_combi, headers):
    url = docker_container_ip + '/api/appliedroles/?rollenid=' + str(rollenid) + '&user_id_name_combi=' + str(
        user_id_name_combi)
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_AppliedAf_by_af_id(af_id, user_id_name_combi, applied_rolle_id, headers):
    url = docker_container_ip + '/api/appliedafs/?af_id=' + str(af_id) \
          + '&applied_rolle_id=' + str(applied_rolle_id) \
          + '&user_id_name_combi=' + str(user_id_name_combi)
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_AppliedGf_by_gf_id(gf_id, user_id_name_combi, applied_rolle_id, applied_af_id, headers):
    url = docker_container_ip + '/api/appliedgfs/?gf_id=' + str(gf_id) \
          + '&user_id_name_combi=' + str(user_id_name_combi) \
          + '&applied_rolle_id=' + str(applied_rolle_id) \
          + '&applied_af_id=' + str(applied_af_id)
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_AppliedTf_by_tf_id(tf_id, user_id_name_combi, applied_rolle_id, applied_af_id, applied_gf_id, headers):
    url = docker_container_ip + '/api/appliedtfs/?tf_id=' + str(tf_id) \
          + '&user_id_name_combi=' + str(user_id_name_combi) \
          + '&applied_rolle_id=' + str(applied_rolle_id) \
          + '&applied_af_id=' + str(applied_af_id) \
          + '&applied_gf_id=' + str(applied_gf_id)
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_tf_by_name(tf_name, headers, request):
    tf_name = tf_name.replace('#', '%23')
    url = docker_container_ip + '/api/tfs/?tf_name=' + tf_name
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_schreibweise_by_name(schreibweise, headers, request):
    schreibweise = schreibweise.replace('#', '%23')
    url = docker_container_ip + '/api/schreibweisen/?schreibweise=' + schreibweise
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_tf_aus_gesamt_by_user_name_af_name_gf_name_tf_name(userid_name, af_name, gf_name, tf_name, headers):
    af_name = af_name.replace('#', '%23')
    gf_name = gf_name.replace('#', '%23')
    tf_name = tf_name.replace('#', '%23')
    url = docker_container_ip + '/api/gesamte/?userid_name=' + userid_name.__str__() + '&af_name=' \
          + af_name + '&gf_name=' + gf_name + '&tf_name=' + tf_name
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_tf_aus_gesamt_by_user_name_af_name_gf_name(userid_name, af_name, gf_name, headers):
    af_name = af_name.replace('#', '%23')
    gf_name = gf_name.replace('#', '%23')
    url = docker_container_ip + '/api/gesamte/?userid_name=' + userid_name.__str__() + '&af_name=' + af_name + '&gf_name=' + gf_name
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_tf_aus_gesamt_by_user_name_af_name(userid_name, af_name, headers):
    af_name = af_name.replace('#', '%23')
    url = docker_container_ip + '/api/gesamte/?userid_name=' + userid_name.__str__() + '&af_name=' + af_name
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_tf_aus_gesamt_by_user_name(userid_name, headers):
    url = docker_container_ip + '/api/gesamte/?userid_name=' + userid_name.__str__()
    json = requests.get(url, headers=headers).json()
    if 'results' in json:
        json = json['results']
    elif 'detail' in json:
        print(json['detail'])
        raise ConnectionError(json['detail'])
    return json


def get_af_description_from_Tblrechteneuvonimport(user, af, gf, tf, headers):
    af = af.replace('#', '%23')
    gf = gf.replace('#', '%23')
    tf = tf.replace('#', '%23')
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
    data = {"userid": user_id, "last_rights_update": last_rights_update}
    try:
        res = requests.patch(url, data=data, headers=headers)
        print("User last_rights_update-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von af_gfs")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def patch_user_rollen(usernameundid_id, rollen_id, headers):
    url = docker_container_ip + '/api/useridundnamen/'
    data = {"usernameundid_id": usernameundid_id, "rollenname": rollen_id}
    try:
        requests.patch(url, data=data, headers=headers)
        print("userHatUserID-rollen-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von af_gfs")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def patch_rolle_afs(rolle_id, af_id, headers):
    url = docker_container_ip + '/api/rollen/'
    data = {"rollen_id": rolle_id, "af_id": af_id}
    try:
        requests.patch(url, data=data, headers=headers)
        print("rolle-afs-patch-erfolg")
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


def patch_tf_schreibweise(tf_id, schreibweise_id, headers):
    url = docker_container_ip + '/api/tfs/'
    data = {"tf_id": tf_id, "schreibweise_id": schreibweise_id}
    try:
        requests.patch(url, data=data, headers=headers)
        print("GF-TFS-patch-erfolg")
        return Response(status=status.HTTP_201_CREATED)
    except ConnectionError:
        print("Error beim Patchen von gf_tfs")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_rolle(rollenname, system, rollenbeschreibung, datum, headers):
    url = docker_container_ip + '/api/rollen/'
    data = {'rollenname': rollenname, 'system': system, 'rollenbeschreibung': rollenbeschreibung,
            'datum': datum}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("role_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von role")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_af(af_name, neu_ab, headers):
    url = docker_container_ip + '/api/afs/'
    data = {'af_name': af_name, 'neu_ab': neu_ab}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("af_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von af")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_gf(data, headers):
    url = docker_container_ip + '/api/afgfs/'
    try:
        res = requests.post(url, data=data, headers=headers)
        print("gf_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von gf")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_tf(data, headers):
    url = docker_container_ip + '/api/tfs/'
    try:
        res = requests.post(url, data=data, headers=headers)
        print("tf_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von tf")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_schreibweise(data, headers):
    url = docker_container_ip + '/api/schreibweisen/'
    try:
        res = requests.post(url, data=data, headers=headers)
        print("tf_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von tf")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_applied_rolle(role, user_id_name_combi, headers):
    url = docker_container_ip + '/api/appliedroles/'
    data = {'model_rolle_id': role['rollenid'], 'userHatUserID_id': user_id_name_combi['id']}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("applied_role_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von applied_role")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_applied_af(af, applied_role, headers):
    url = docker_container_ip + '/api/appliedafs/'
    data = {'model_af_id': af['id'], 'applied_role_id': applied_role['id']}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("applied_af_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von applied_af")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_applied_gf(gf, applied_af, headers):
    url = docker_container_ip + '/api/appliedgfs/'
    data = {'model_gf_id': gf['id'], 'applied_af_id': applied_af['id']}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("applied_gf_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von applied_gf")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def create_applied_tf(tf, applied_gf, headers):
    url = docker_container_ip + '/api/appliedtfs/'
    data = {'model_tf_id': tf['id'], 'applied_gf_id': applied_gf['id']}
    try:
        res = requests.post(url, data=data, headers=headers)
        print("applied_tf_create-erfolg")
        return res
    except ConnectionError:
        print("Error beim Create von applied_tf")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def clear_user_applied_tf(userid, headers):
    url = docker_container_ip + '/api/appliedtfs/'
    data = {'bulk-delete':True,'userid':userid}
    try:
        res = requests.patch(url, data=data, headers=headers)
        print("applied_tf_bulk-delete-erfolg")
        return res
    except ConnectionError:
        print("Error beim BULK-DELETE von applied_tf")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def clear_user_applied_gf(userid, headers):
    url = docker_container_ip + '/api/appliedgfs/'
    data = {'bulk-delete':True,'userid':userid}
    try:
        res = requests.patch(url, data=data, headers=headers)
        print("applied_gf_bulk-delete-erfolg")
        return res
    except ConnectionError:
        print("Error beim BULK-DELETE von applied_gf")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def clear_user_applied_af(userid, headers):
    url = docker_container_ip + '/api/appliedafs/'
    data = {'bulk-delete':True,'userid':userid}
    try:
        res = requests.patch(url, data=data, headers=headers)
        print("applied_af_bulk-delete-erfolg")
        return res
    except ConnectionError:
        print("Error beim BULK-DELETE von applied_af")
    return Response(status=status.HTTP_400_BAD_REQUEST)


def clear_user_applied_roles(userid, headers):
    url = docker_container_ip + '/api/appliedroles/'
    data = {'bulk-delete':True,'userid':userid}
    try:
        res = requests.patch(url, data=data, headers=headers)
        print("applied_roles_bulk-delete-erfolg")
        return res
    except ConnectionError:
        print("Error beim BULK-DELETE von applied_roles")
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


def presort_rollen(user_data, headers):
    for rolle_url in user_data['rollen']:
        model_rolle = get_by_url(rolle_url, headers)
        if model_rolle['rollenname'] == 'Keine Rolle':
            user_data['rollen'].append(user_data['rollen'].pop(user_data['rollen'].index(rolle_url)))
            break
    return user_data


def get_user_info_dict_for_all_applied_userids(headers, request, user_json_data):
    user_info = []
    for user_url in user_json_data['userid_name']:
        userid_name_data = get_by_url(user_url, headers)
        user_userid_combination = get_full_user_userid_name_combination(headers, user_json_data['id'],
                                                                        userid_name_data['id'], request)[0]
        user_info.append({'user_data': userid_name_data, 'rights_data': user_userid_combination})
    return user_info

def connect_user_and_profiles(user, headers):
    #TODO: connect user and userid_und_name
    username_numerics = user.username[2:]
    print(username_numerics)
    userid_names = TblUserIDundName.objects.filter(userid__endswith=username_numerics)
    for userid_name in userid_names:
        if not userid_name.id in user.userid_name:
            user.userid_name.add(userid_name.id)


def clear_personal_rights_models(user_info, headers, request):
    rights_data = user_info['rights_data']
    clear_user_applied_tf(rights_data['id'],headers)
    clear_user_applied_gf(rights_data['id'],headers)
    clear_user_applied_af(rights_data['id'],headers)
    clear_user_applied_roles(rights_data['id'],headers)



def update_personal_right_models(user_info, headers, request):
    print(user_info)
    user_data = user_info['user_data']
    rights_data = user_info['rights_data']
    user_tfs = get_tf_aus_gesamt_by_user_name(user_data['id'], headers)

    cached_roles = dict()
    cached_afs = dict()
    cached_gfs = dict()
    cached_tfs = dict()
    cached_schreibweisen = dict()

    cached_applied_roles = dict()
    cached_applied_afs = dict()
    cached_applied_gfs = dict()
    cached_applied_tfs = dict()

    cached_tf_hat_schreibweise = dict()
    cached_gf_hat_tf = dict()
    cached_af_hat_gf = dict()
    cached_rolle_hat_af = dict()
    cached_user_hat_rolle = dict()

    roles_changed = True
    for tf in user_tfs:

        af_name = tf['enthalten_in_af']
        if not af_name in cached_afs:
            model_af = get_af_by_name(af_name, headers, request)
            if not model_af:
                res = create_af(af_name, datetime.datetime.now(), headers)
                model_af = json.loads(res.text)
            else:
                model_af = model_af[0]
            cached_afs[af_name] = model_af
        else:
            model_af = cached_afs.get(af_name)

        gf_name = tf['gf']
        if not gf_name in cached_gfs:
            model_gf = get_gf_by_name_and_af_name(gf_name, af_name, headers, request)
            if not model_gf:
                data = {'name_gf_neu': gf_name, 'name_af_neu': af_name, 'kommentar': 'Kein Kommentar',
                        'zielperson': 'Keine Zielperson', 'af_text': 'Keine af_text', 'gf_text': 'Keine gf_text',
                        'af_langtext': 'Keine af_langtext', 'af_ausschlussgruppen': 'Keine af_ausschlussgruppen',
                        'af_einschlussgruppen': 'Keine af_einschlussgruppen',
                        'af_sonstige_vergabehinweise': 'Keine af_sonstige_vergabehinweise', 'geloescht': 0,
                        'kannweg': 0,
                        'modelliert': datetime.datetime.now()}
                res = create_gf(data, headers)
                model_gf = json.loads(res.text)
            else:
                model_gf = model_gf[0]
            cached_gfs[gf_name] = model_gf
        else:
            model_gf = cached_gfs.get(gf_name)

        tf_name = tf['tf']
        tf_name_lower = tf_name.lower()
        if not tf_name_lower in cached_tfs:
            model_tf = get_tf_by_name(tf_name_lower, headers, request)
            if not model_tf:
                data = {'tf': tf_name_lower, 'tf_beschreibung': tf['tf_beschreibung'],
                        'tf_kritikalitaet': tf['tf_kritikalitaet'],
                        'tf_eigentuemer_org': tf['tf_eigentuemer_org'], 'plattform': tf['plattform'],
                        'vip_kennzeichen': tf['vip_kennzeichen'], 'zufallsgenerator': tf['zufallsgenerator'],
                        'direct_connect': tf['direct_connect'], 'datum': tf['datum'], 'geloescht': tf['geloescht'],
                        'gefunden': tf['gefunden'], 'wiedergefunden': tf['wiedergefunden'],
                        'geaendert': tf['geaendert'],
                        'nicht_ai': tf['nicht_ai'], 'patchdatum': tf['patchdatum'],
                        'wertmodellvorpatch': tf['wertmodellvorpatch'], 'loeschdatum': tf['loeschdatum'],
                        'letzte_aenderung': tf['letzte_aenderung']}
                res = create_tf(data, headers)
                model_tf = json.loads(res.text)
            else:
                model_tf = model_tf[0]
            cached_tfs[tf_name_lower] = model_tf
        else:
            model_tf = cached_tfs.get(tf_name_lower)

        if tf_name != tf_name_lower:
            if not tf_name in cached_schreibweisen:
                schreibweise = get_schreibweise_by_name(tf_name, headers, request)
                if not schreibweise:
                    data = {'schreibweise': tf_name}
                    res = create_schreibweise(data, headers)
                    schreibweise = json.loads(res.text)
                else:
                    schreibweise = schreibweise[0]
                cached_schreibweisen[tf_name] = schreibweise
            else:
                schreibweise = cached_schreibweisen.get(tf_name)

            tf_hat_schreibweise_key = "{}_{}".format(model_tf['id'],schreibweise['id'])
            if not tf_hat_schreibweise_key in cached_tf_hat_schreibweise:
                tf_hat_schreibweise = get_tf_hat_schreibweise_by_ids(model_tf['id'], schreibweise['id'], headers)
                if not tf_hat_schreibweise:
                    patch_tf_schreibweise(model_tf['id'],schreibweise['id'],headers)
                cached_tf_hat_schreibweise[tf_hat_schreibweise_key] = tf_hat_schreibweise

        model_gf_id = model_gf['id']
        model_tf_id = model_tf['id']
        gf_hat_tf_key = "{}_{}".format(model_gf_id, model_tf_id)
        if not gf_hat_tf_key in cached_gf_hat_tf:
            gf_hat_tf = get_gf_hat_tf_by_ids(model_gf['id'], model_tf['id'], headers)
            if not gf_hat_tf:
                patch_gf_tfs(model_gf['id'], model_tf['id'], headers)
            cached_gf_hat_tf[gf_hat_tf_key] = gf_hat_tf

        model_af_id = model_af['id']
        af_hat_gf_key = "{}_{}".format(model_af_id, model_gf_id)
        if not af_hat_gf_key in cached_af_hat_gf:
            af_hat_gf = get_af_hat_gf_by_ids(model_af['id'], model_gf['id'], headers)
            if not af_hat_gf:
                patch_af_gfs(model_af['id'], model_gf['id'], headers)
            cached_af_hat_gf[af_hat_gf_key] = af_hat_gf

        if roles_changed:
            user_rollen = get_user_roles(headers, user_data['userid'], request)

        found = False
        for user_role in user_rollen:
            rollenname = user_role['rollenname']
            rolle_hat_af_key = "{}_{}".format(rollenname, model_af_id)
            if not rolle_hat_af_key in cached_rolle_hat_af:
                rolle_hat_af = get_rolle_hat_af_by_ids(rollenname, model_af_id, headers)
                cached_rolle_hat_af[rolle_hat_af_key] = rolle_hat_af
            else:
                rolle_hat_af = cached_rolle_hat_af.get(rolle_hat_af_key)
            if rolle_hat_af:
                found = True
                break

        if not found:
            if not 'Keine Rolle' in cached_roles:
                keine_rolle = get_rolle_by_rollenname('Keine Rolle', headers, request)
                if not keine_rolle:
                    res = create_rolle('Keine Rolle', 'Kein System', 'Keine Rollenbeschreibung',
                                       datetime.datetime.now(),
                                       headers)
                    user_role = json.loads(res.text)
                    cached_roles['Keine Rolle'] = user_role
                else:
                    user_role = keine_rolle[0]
                    cached_roles['Keine Rolle'] = user_role
                roles_changed = True
            else:
                user_role = cached_roles.get('Keine Rolle')
                roles_changed = False
        else:
            if not rollenname in cached_roles:
                user_role = get_rolle_by_rollenname(rollenname, headers, request)[0]
                cached_roles[rollenname] = user_role
                roles_changed = True
            else:
                user_role = cached_roles.get(rollenname)
                roles_changed = False

        rollenid = user_role['rollenid']
        user_hat_userid_id = rights_data['id']
        if not rollenid in cached_applied_roles:
            applied_rolle = get_AppliedRolle_by_rollenid(rollenid, user_hat_userid_id, headers)
            if not applied_rolle:
                res = create_applied_rolle(user_role, rights_data, headers)
                applied_rolle = json.loads(res.text)
                patch_userhatuseridundnamen_rollen(user_hat_userid_id, applied_rolle['id'], headers)
            else:
                applied_rolle = applied_rolle[0]
            cached_applied_roles[rollenid] = applied_rolle
        else:
            applied_rolle = cached_applied_roles.get(rollenid)

        if not model_af_id in cached_applied_afs:
            applied_af = get_AppliedAf_by_af_id(model_af_id, user_hat_userid_id, applied_rolle['id'], headers)
            if not applied_af:
                res = create_applied_af(model_af, applied_rolle, headers)
                applied_af = json.loads(res.text)
                patch_applied_rolle_applied_afs(applied_rolle['id'], applied_af['id'], headers)
            else:
                applied_af = applied_af[0]
            cached_applied_afs[model_af_id] = applied_af
        else:
            applied_af = cached_applied_afs.get(model_af_id)

        if not model_gf_id in cached_applied_gfs:
            applied_gf = get_AppliedGf_by_gf_id(model_gf_id, user_hat_userid_id, applied_rolle['id'], applied_af['id'],
                                                headers)
            if not applied_gf:
                res = create_applied_gf(model_gf, applied_af, headers)
                applied_gf = json.loads(res.text)
                patch_applied_af_applied_gfs(applied_af['id'], applied_gf['id'], headers)
            else:
                applied_gf = applied_gf[0]
            cached_applied_gfs[model_gf_id] = applied_gf
        else:
            applied_gf = cached_applied_gfs.get(model_gf_id)

        if not model_tf_id in cached_applied_tfs:
            applied_tf = get_AppliedTf_by_tf_id(model_tf_id, user_hat_userid_id, applied_rolle['id'], applied_af['id'],
                                                applied_gf['id'], headers)
            if not applied_tf:
                res = create_applied_tf(model_tf, applied_gf, headers)
                applied_tf = json.loads(res.text)
                patch_applied_gf_applied_tfs(applied_gf['id'], applied_tf['id'], headers)
            else:
                applied_tf = applied_tf[0]
            cached_applied_tfs[model_tf_id] = applied_tf
        else:
            applied_tf = cached_applied_tfs.get(model_tf_id)

    print(len(user_tfs), user_tfs)


def prepareJSONdata(identity, user_info, compareUser, headers, request, legend_data, cached_af_descriptions):
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
    userList = []
    rolleList = []
    afList = []
    gfList = []
    tfList = []
    # user_json_data['children'] = user_json_data.pop('user_afs')
    user_detail_data = []
    graph_data = dict()
    graph_data['children'] = []
    counts = {'user': 0, 'roles': 0, 'afs': 0, 'gfs': 0, 'tfs': 0, }

    for u in user_info:
        user = u['user_data'].copy()
        user['name'] = user['userid']
        user['children'] = []
        counts['user'] += 1
        user_userid_combination = u['rights_data'].copy()
        user['user_userid_combi_id'] = user_userid_combination['id']
        graph_data['children'].append(user)
        for rolle in user_userid_combination['rollen']:
            # rolle = get_by_url(rolle, headers)
            if rolle['applied_afs']:
                rolle_details = rolle['model_rolle_id']
                # rolle_details = get_by_url(rolle['model_rolle_id'],headers)
                rolle['name'] = rolle_details['rollenname']
                rolle['description'] = rolle_details['rollenbeschreibung']
                rolle['children'] = []
                user['children'].append(rolle)
                counts['roles'] += 1
                af_old = None
                for af in rolle['applied_afs']:
                    # af = get_by_url(af, headers)
                    if af['applied_gfs']:
                        if type(af['model_af_id']) is str:
                            af['model_af_id'] = get_by_url(af['model_af_id'], headers)
                        af_details = af['model_af_id']
                        af['name'] = af_details['af_name']
                        af['children'] = []
                        rolle['children'].append(af)
                        counts['afs'] += 1

                        gf_old = None
                        for gf in af['applied_gfs']:
                            # gf = get_by_url(gf, headers)
                            if gf['applied_tfs']:
                                if type(gf['model_gf_id']) is str:
                                    gf['model_gf_id'] = get_by_url(gf['model_gf_id'], headers)
                                gf_details = gf['model_gf_id']
                                gf['name'] = gf_details['name_gf_neu']
                                gf['children'] = []
                                counts['gfs'] += 1
                                af['children'].append(gf)

                                for tf in gf['applied_tfs']:
                                    # tf = get_by_url(tf, headers)
                                    if type(tf['model_tf_id']) is str:
                                        tf['model_tf_id'] = get_by_url(tf['model_tf_id'], headers)
                                    tf_details = tf['model_tf_id']
                                    if tf_details['tf_schreibweise']:
                                        tf['name'] = tf_details['tf_schreibweise'][0]['schreibweise']
                                    else:
                                        tf['name'] = tf_details['tf']

                                    tf['size'] = 3000
                                    gf['children'].append(tf)
                                    counts['tfs'] += 1
                                    plattform = tf_details['plattform']
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

                                    tfList.append(tf['name'])
                                    gfList.append(gf['name'])
                                    afList.append(af['name'])
                                    rolleList.append(rolle['name'])
                                    userList.append(user['name'])

                                    if not af['name'] in cached_af_descriptions:
                                        af_description_helper = get_af_description_from_Tblrechteneuvonimport(
                                            user['name'],
                                            af['name'],
                                            gf['name'],
                                            tf['name'],
                                            headers)
                                        if not af_description_helper:
                                            af['description'] = "Keine Beschreibung vorhanden!"
                                        else:
                                            af['description'] = af_description_helper[0]['af_beschreibung']
                                        cached_af_descriptions[af['name']] = af_description_helper
                                    else:
                                        af_description_helper = cached_af_descriptions.get(af['name'])
                                    if gf['name'] != gf_old:
                                        if 'gf_beschreibung' in tf_details:
                                            if not tf_details['gf_beschreibung']:
                                                gf['description'] = "Keine Beschreibung vorhanden!"
                                            else:
                                                gf['description'] = tf_details['gf_beschreibung']
                                        else:
                                            gf['description'] = "Keine Beschreibung vorhanden!"
                                        gf_old = gf['name']
                            if gf in af['children'] and not gf['children']:
                                af['children'].remove(gf)
                                counts['gfs'] -= 1
                    if af in rolle['children'] and not af['children']:
                        rolle['children'].remove(af)
                        counts['afs'] -= 1
                if not rolle['children']:
                    counts['roles'] -= 1
    if not compareUser:
        scatterData.sort(key=lambda r: r["af_applied"])
        i = 0
        for e in scatterData:
            e["index"] = i
            i += 1

    data = zip(tfList, gfList, afList, rolleList, userList)
    list_data = list(data)
    return graph_data, scatterData, counts, cached_af_descriptions, list_data


def prepareDeleteJSONdata(user_info, request, headers, legend_data, cached_af_descriptions):
    '''
    prepare delete_list for display as circlepacking
    :param delete_list:
    :return:
    '''
    delete_graph_data = {"children": []}
    delete_list_with_category = []
    tfList = []
    gfList = []
    afList = []
    rolleList = []
    userList = []
    single_rights_count = 0
    for u in user_info:
        user = u['user_data'].copy()
        user['name'] = user['userid']
        user['children'] = []
        user_userid_combination = u['rights_data'].copy()
        user['user_userid_combi_id'] = user_userid_combination['id']
        delete_graph_data['children'].append(user)
        for rolle in user_userid_combination['delete_list']:
            # rolle = get_by_url(rolle, headers)
            rolle_details = rolle['model_rolle_id']
            # rolle_details = get_by_url(rolle['model_rolle_id'], headers)
            rolle['name'] = rolle_details['rollenname']
            rolle['description'] = rolle_details['rollenbeschreibung']
            rolle['children'] = []
            user['children'].append(rolle)
            af_old = None
            for af in rolle['applied_afs']:
                # af = get_by_url(af, headers)
                if af['applied_gfs']:
                    af_details = af['model_af_id']
                    # af_details = get_by_url(af['model_af_id'], headers)
                    af['name'] = af_details['af_name']
                    af['children'] = []
                    rolle['children'].append(af)

                    gf_old = None
                    for gf in af['applied_gfs']:
                        # gf = get_by_url(gf, headers)
                        if gf['applied_tfs']:
                            gf_details = gf['model_gf_id']
                            # gf_details = get_by_url(gf['model_gf_id'], headers)
                            gf['name'] = gf_details['name_gf_neu']
                            gf['children'] = []
                            af['children'].append(gf)

                            for tf in gf['applied_tfs']:
                                # tf = get_by_url(tf, headers)
                                tf_details = tf['model_tf_id']
                                # tf_details = get_by_url(tf['model_tf_id'], headers)
                                if tf_details['tf_schreibweise']:
                                    tf['name'] = tf_details['tf_schreibweise'][0]['schreibweise']
                                else:
                                    tf['name'] = tf_details['tf']
                                tf['size'] = 3000
                                gf['children'].append(tf)
                                single_rights_count += 1
                                plattform = tf_details['plattform']
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
                                if not af['name'] in cached_af_descriptions:
                                    af_description_helper = get_af_description_from_Tblrechteneuvonimport(user['name'],
                                                                                                          af['name'],
                                                                                                          gf['name'],
                                                                                                          tf['name'],
                                                                                                          headers)
                                    if not af_description_helper:
                                        af['description'] = "Keine Beschreibung vorhanden!"
                                    else:
                                        af['description'] = af_description_helper[0]['af_beschreibung']
                                    cached_af_descriptions[af['name']] = af_description_helper
                                else:
                                    af_description_helper = cached_af_descriptions.get(af['name'])
                                if gf['name'] != gf_old:
                                    if 'gf_beschreibung' in tf_details:
                                        if not tf_details['gf_beschreibung']:
                                            gf['description'] = "Keine Beschreibung vorhanden!"
                                        else:
                                            gf['description'] = tf_details['gf_beschreibung']
                                    else:
                                        gf['description'] = "Keine Beschreibung vorhanden!"
                                    gf_old = gf['name']
                                tfList.append(tf['name'])
                                gfList.append(gf['name'])
                                afList.append(af['name'])
                                rolleList.append(rolle['name'])
                                userList.append(user['name'])
                                if tf['deleted'] and not tf['requested']:
                                    delete_list_with_category.append({'right': tf, 'type': 'tf'})
                            if gf['deleted'] and not gf['requested']:
                                delete_list_with_category.append({'right': gf, 'type': 'gf'})
                    if af['deleted'] and not af['requested']:
                        delete_list_with_category.append({'right': af, 'type': 'af'})
            if rolle['deleted'] and not rolle['requested']:
                delete_list_with_category.append({'right': rolle, 'type': 'rolle'})

    data = zip(tfList, gfList, afList, rolleList, userList)
    list_data = list(data)

    return delete_graph_data, delete_list_with_category, single_rights_count, cached_af_descriptions, list_data


def prepareTransferJSONdata(user_info, request, headers, legend_data, cached_af_descriptions):
    '''
    method to prepare transferlist-data for display as circlepacking
    :param transfer_json_data:
    :return:
    '''
    tfList = []
    gfList = []
    afList = []
    rolleList = []
    userList = []
    transfer_graph_data = {"children": []}
    transfer_list_with_category = []
    single_rights_count = 0
    for u in user_info:
        user = u['user_data'].copy()
        user['name'] = user['userid']
        user['children'] = []
        user_userid_combination = u['rights_data'].copy()
        user['user_userid_combi_id'] = user_userid_combination['id']
        transfer_graph_data['children'].append(user)
        for rolle in user_userid_combination['transfer_list']:
            # rolle = get_by_url(rolle, headers)
            rolle_details = rolle['model_rolle_id']
            # rolle_details = get_by_url(rolle['model_rolle_id'], headers)
            rolle['name'] = rolle_details['rollenname']
            rolle['description'] = rolle_details['rollenbeschreibung']
            rolle['children'] = []
            user['children'].append(rolle)
            for af in rolle['applied_afs']:
                # af = get_by_url(af, headers)
                if af['applied_gfs']:
                    af_details = af['model_af_id']
                    # af_details = get_by_url(af['model_af_id'], headers)
                    af['name'] = af_details['af_name']
                    af['children'] = []
                    rolle['children'].append(af)

                    gf_old = None
                    for gf in af['applied_gfs']:
                        # gf = get_by_url(gf, headers)
                        if gf['applied_tfs']:
                            gf_details = gf['model_gf_id']
                            # gf_details = get_by_url(gf['model_gf_id'], headers)
                            gf['name'] = gf_details['name_gf_neu']
                            gf['children'] = []
                            af['children'].append(gf)

                            for tf in gf['applied_tfs']:
                                # tf = get_by_url(tf, headers)
                                tf_details = tf['model_tf_id']
                                # tf_details = get_by_url(tf['model_tf_id'], headers)
                                if tf_details['tf_schreibweise']:
                                    tf['name'] = tf_details['tf_schreibweise'][0]['schreibweise']
                                else:
                                    tf['name'] = tf_details['tf']
                                tf['size'] = 3000
                                gf['children'].append(tf)
                                single_rights_count += 1
                                plattform = tf_details['plattform']
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
                                if not af['name'] in cached_af_descriptions:
                                    af_description_helper = get_af_description_from_Tblrechteneuvonimport(user['name'],
                                                                                                          af['name'],
                                                                                                          gf['name'],
                                                                                                          tf['name'],
                                                                                                          headers)
                                    if not af_description_helper:
                                        af['description'] = "Keine Beschreibung vorhanden!"
                                    else:
                                        af['description'] = af_description_helper[0]['af_beschreibung']
                                    cached_af_descriptions[af['name']] = af_description_helper
                                else:
                                    af_description_helper = cached_af_descriptions.get(af['name'])
                                if gf['name'] != gf_old:
                                    if 'gf_beschreibung' in tf_details:
                                        if not tf_details['gf_beschreibung']:
                                            gf['description'] = "Keine Beschreibung vorhanden!"
                                        else:
                                            gf['description'] = tf_details['gf_beschreibung']
                                    else:
                                        gf['description'] = "Keine Beschreibung vorhanden!"
                                    gf_old = gf['name']
                                tfList.append(tf['name'])
                                gfList.append(gf['name'])
                                afList.append(af['name'])
                                rolleList.append(rolle['name'])
                                userList.append(user['name'])
                                if tf['transfered'] and not tf['requested']:
                                    transfer_list_with_category.append({'right': tf, 'type': 'tf'})
                            if gf['transfered'] and not gf['requested']:
                                transfer_list_with_category.append({'right': gf, 'type': 'gf'})
                    if af['transfered'] and not af['requested']:
                        transfer_list_with_category.append({'right': af, 'type': 'af'})
            if rolle['transfered'] and not rolle['requested']:
                transfer_list_with_category.append({'right': rolle, 'type': 'rolle'})

    data = zip(tfList, gfList, afList, rolleList, userList)
    list_data = list(data)
    return transfer_graph_data, transfer_list_with_category, single_rights_count, cached_af_descriptions, list_data


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
        requesting_user_id = \
            TblUserIDundName.objects.filter(userid=data['requesting_user[value]'].upper()).values_list('id', flat=True)[
                0]
        requesting_user_userid_name_combi = UserHatTblUserIDundName.objects.filter(
            userid_name_id=requesting_user_id).get()
        compare_user_id = \
            TblUserIDundName.objects.filter(userid=data['compare_user[value]'].upper()).values_list('id', flat=True)[0]
        compare_user_userid_name_combi = UserHatTblUserIDundName.objects.filter(userid_name_id=compare_user_id).get()
        for obj in objects_to_change:
            obj_data = {'requesting_user': data['requesting_user[value]'],
                        'compare_user': data['compare_user[value]'],
                        'action': obj[0]['value'], 'right_name': obj[1]['value'], 'right_type': obj[2]['value'],
                        'reason_for_action': obj[3]['value']}
            serializer = self.get_serializer(data=obj_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            cr = ChangeRequests.objects.get(id=serializer.data['pk'])
            cr.requesting_user_hat_userid_name_combination = requesting_user_userid_name_combi
            cr.compare_user_hat_userid_name_combination = compare_user_userid_name_combi
            cr.save()
            added_requests.append(serializer.data['pk'])
        headers = self.get_success_headers(serializer.data)
        return Response(json.dumps(added_requests), status=status.HTTP_201_CREATED, headers=headers)


class TblRollenViewSet(viewsets.ModelViewSet):
    '''
        API-Rollen ViewSet
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = TblRollenSerializer

    def get_queryset(self):
        if 'rollenname' in self.request.GET:
            rollenname = self.request.GET['rollenname']
            return TblRollen.objects.filter(rollenname__iexact=rollenname).order_by('rollenid')
        return TblRollen.objects.all()

    def create(self, request, *args, **kwargs):
        print("In RollenViewSet-Create")
        serializer = TblRollenSerializer(data=request.data)
        if serializer.is_valid():
            rolle = serializer.save()
            return Response(data=TblRollenSerializer(rolle, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        print("in rolle API-Viewset-PATCH-Method")
        pk = request.POST['rollen_id']
        rolle_to_update = TblRollen.objects.get(rollenname=pk)
        update_afs = rolle_to_update.afs
        update_afs.add(request.POST['af_id'])
        return Response(status=status.HTTP_201_CREATED)


class TblUebersichtAfGfsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblUebersichtAfGfsSerializer

    def get_queryset(self):
        if 'gf_name' in self.request.GET and 'af_name' in self.request.GET:
            gf_name = self.request.GET['gf_name'].replace('%23', '#')
            af_name = self.request.GET['af_name'].replace('%23', '#')
            filtered = TblUebersichtAfGfs.objects.filter(name_gf_neu__iexact=gf_name).filter(
                name_af_neu__iexact=af_name).order_by('name_gf_neu')
            return filtered
        elif 'gf_name' in self.request.GET and not 'af_name' in self.request.GET:
            gf_name = self.request.GET['gf_name'].replace('%23', '#')
            filtered = TblUebersichtAfGfs.objects.filter(name_gf_neu__iexact=gf_name).order_by('id')
            return filtered
        elif 'af_name' in self.request.GET and not 'gf_name' in self.request.GET:
            af_name = self.request.GET['af_name'].replace('%23', '#')
            return TblUebersichtAfGfs.objects.filter(name_af_neu__iexact=af_name).order_by('id')

        return TblUebersichtAfGfs.objects.all()

    def patch(self, request, *args, **kwargs):
        print("in UebersichtAfGfs API-Viewset-PATCH-Method")
        pk = request.POST['gf_id']
        gf_to_update = TblUebersichtAfGfs.objects.get(id=pk)
        update_tfs = gf_to_update.tfs
        update_tfs.add(request.POST['tf_id'])
        return Response(status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        print("In GFViewSet-Create")
        serializer = TblUebersichtAfGfsSerializer(data=request.data)
        if serializer.is_valid():
            gf = serializer.save()
            return Response(data=TblUebersichtAfGfsSerializer(gf, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TblOrgaViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblOrgaSerializer
    pagination_class = None

    def get_queryset(self):
        return TblOrga.objects.all()


class TblUserIDundNameViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblUserIDundNameSerializer
    pagination_class = None

    def get_queryset(self):
        if 'field' in self.request.GET:
            field = self.request.GET['field']
            data = TblUserIDundName.objects.order_by(field).values_list(field, flat=True).distinct()
            qs_all = []
            for d in data:
                if field == 'zi_organisation':
                    qs = TblUserIDundName.objects.filter(zi_organisation=d)
                elif field == 'abteilung':
                    qs = TblUserIDundName.objects.filter(abteilung=d)
                elif field == 'gruppe':
                    qs = TblUserIDundName.objects.filter(gruppe=d)
                qs_list = list(qs)
                qs_all.append(qs_list[0])
            return qs_all
        elif 'search_what' in self.request.GET:
            search_what = self.request.GET["search_what"]
            user_search = self.request.GET["userSearch"]
            if search_what == "identity":
                users = TblUserIDundName.objects.filter(userid__istartswith=user_search).order_by('name')
            elif search_what == "name":
                users = TblUserIDundName.objects.filter(name__istartswith=user_search).order_by('name')
            if 'orga' in self.request.GET:
                orga = self.request.GET['orga']
                users = users.filter(orga__team=orga)
            if 'zi_organisation' in self.request.GET:
                zi_organisation = self.request.GET['zi_organisation']
                users = users.filter(zi_organisation=zi_organisation)
            if 'abteilung' in self.request.GET:
                abteilung = self.request.GET['abteilung']
                users = users.filter(abteilung=abteilung)
            if 'gruppe' in self.request.GET:
                gruppe = self.request.GET['gruppe']
                users = users.filter(gruppe=gruppe)
            return users
        elif 'xvnumber' in self.request.GET:
            xvnumber = self.request.GET['xvnumber']
            user_id_und_name = TblUserIDundName.objects.filter(userid=xvnumber)
            return user_id_und_name

        return TblUserIDundName.objects.all()

    def patch(self, request, *args, **kwargs):
        print("in UserIdundName API-Viewset-PATCH-Method")
        pk = request.POST['usernameundid_id']
        useridundname_to_update = TblUserIDundName.objects.get(id=pk)
        update_rollen = useridundname_to_update.rollen
        update_rollen.add(request.POST['rollenname'])
        return Response(status=status.HTTP_201_CREATED)


class TblPlattformViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblPlattformSerializer

    def get_queryset(self):
        return TblPlattform.objects.all()


class TblSchreibweisenViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblSchreibweisenSerializer
    pagination_class = None

    def get_queryset(self):
        if 'schreibweise' in self.request.GET:
            schreibweise = self.request.GET['schreibweise'].replace('%23', '#')
            filtered = TblSchreibweisen.objects.filter(schreibweise=schreibweise)
            return filtered
        return TblSchreibweisen.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = TblSchreibweisenSerializer(data=request.data)
        if serializer.is_valid():
            schreibweise = serializer.save()
            return Response(data=TblSchreibweisenSerializer(schreibweise, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TblTfViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblTfSerializer
    pagination_class = None

    def get_queryset(self):
        if 'tf_name' in self.request.GET:
            tf_name = self.request.GET['tf_name'].replace('%23', '#')
            filtered = TblTf.objects.filter(tf__iexact=tf_name) \
                .order_by('tf')
            return filtered
        return TblTf.objects.all()

    def create(self, request, *args, **kwargs):
        print("In TFViewSet-Create")
        serializer = TblTfSerializer(data=request.data)
        if serializer.is_valid():
            tf = serializer.save()
            return Response(data=TblTfSerializer(tf, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        print("in TblTf API-Viewset-PATCH-Method")
        pk = request.POST['tf_id']
        tf_to_update = TblTf.objects.get(id=pk)
        update_schreibweise = tf_to_update.tf_schreibweise
        update_schreibweise.add(request.POST['schreibweise_id'])
        return Response(status=status.HTTP_201_CREATED)

class TblGesamtViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblGesamtSerializer
    pagination_class = None

    def get_queryset(self):
        if 'userid_name' in self.request.GET and not 'af_name' in self.request.GET \
                and not 'gf_name' in self.request.GET and not 'tf_name' in self.request.GET:
            userid_name = self.request.GET['userid_name']
            filtered = TblGesamt.objects.filter(userid_name_id=userid_name).order_by('id')
            return filtered
        elif 'userid_name' in self.request.GET and 'af_name' in self.request.GET \
                and 'gf_name' in self.request.GET and 'tf_name' in self.request.GET:
            userid_name = self.request.GET['userid_name']
            af_name = self.request.GET['af_name'].replace('%23', '#')
            gf_name = self.request.GET['gf_name'].replace('%23', '#')
            tf_name = self.request.GET['tf_name'].replace('%23', '#')
            filtered = TblGesamt.objects.filter(userid_name_id=userid_name).filter(enthalten_in_af__iexact=af_name) \
                .filter(gf__iexact=gf_name).filter(tf__iexact=tf_name).order_by('id')
            return filtered
        elif 'userid_name' in self.request.GET and 'af_name' in self.request.GET \
                and 'gf_name' in self.request.GET and not 'tf_name' in self.request.GET:
            userid_name = self.request.GET['userid_name']
            af_name = self.request.GET['af_name'].replace('%23', '#')
            gf_name = self.request.GET['gf_name'].replace('%23', '#')
            filtered = TblGesamt.objects.filter(userid_name_id=userid_name).filter(enthalten_in_af__iexact=af_name) \
                .filter(gf__iexact=gf_name).order_by('id')
            return filtered
        elif 'userid_name' in self.request.GET and 'af_name' in self.request.GET \
                and not 'gf_name' in self.request.GET and not 'tf_name' in self.request.GET:
            userid_name = self.request.GET['userid_name']
            af_name = self.request.GET['af_name'].replace('%23', '#')
            filtered = TblGesamt.objects.filter(userid_name_id=userid_name).filter(enthalten_in_af__iexact=af_name) \
                .order_by('id')
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
        if 'af_name' in self.request.GET:
            af_name = self.request.GET['af_name'].replace('%23', '#')
            filtered = TblAfliste.objects.filter(af_name__iexact=af_name).order_by('af_name')
            return filtered
        return TblAfliste.objects.all()

    def patch(self, request, *args, **kwargs):
        print("in AfListe API-Viewset-PATCH-Method")
        pk = request.POST['af_id']
        af_to_update = TblAfliste.objects.get(id=pk)
        update_gfs = af_to_update.gfs
        update_gfs.add(request.POST['gf_id'])
        return Response(status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        print("In AFViewSet-Create")
        serializer = TblAflisteSerializer(data=request.data)
        if serializer.is_valid():
            af = serializer.save()
            return Response(data=TblAflisteSerializer(af, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            userid_name = self.request.GET['userid_name'].lower()
            af_name = self.request.GET['af_name'].replace('%23', '#')
            gf_name = self.request.GET['gf_name'].replace('%23', '#')
            tf_name = self.request.GET['tf_name'].replace('%23', '#')
            filtered = Tblrechteneuvonimport.objects.filter(identitaet=userid_name) \
                .filter(af_anzeigename__iexact=af_name).filter(gf_name__iexact=gf_name).filter(tf_name__iexact=tf_name)
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
            if user_pk == 'None':
                filtered = UserHatTblUserIDundName.objects.filter(userid_name_id=userid_name_pk)
            elif userid_name_pk == 'None':
                filtered = UserHatTblUserIDundName.objects.filter(user_name=user_pk)
            else:
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
        if 'user_id' in self.request.GET and not 'rollenname' in self.request.GET:
            user_id = self.request.GET['user_id']
            filtered = TblUserhatrolle.objects.filter(userid=user_id)
            return filtered
        if 'user_id' in self.request.GET and 'rollenname' in self.request.GET:
            user_id = self.request.GET['user_id']
            rollenname = self.request.GET['rollenname']
            filtered = TblUserhatrolle.objects.filter(userid=user_id) \
                .filter(rollenname=rollenname)
            return filtered

        return TblUserhatrolle.objects.all()


class TblRollehatafViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblRollehatafSerializer

    def get_queryset(self):
        if 'rollenname' in self.request.GET and 'af_id' in self.request.GET:
            af_id = self.request.GET['af_id']
            rollenname = self.request.GET['rollenname']
            filtered = TblRollehataf.objects.filter(rollenname=rollenname) \
                .filter(af=af_id)
            return filtered
        return TblRollehataf.objects.all()


class TblAfHatGfViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAfHatGfSerializer

    def get_queryset(self):
        if 'af_id' in self.request.GET and 'gf_id' in self.request.GET:
            af_id = self.request.GET['af_id']
            gf_id = self.request.GET['gf_id']
            filtered = TblAfHatGf.objects.filter(af_id=af_id) \
                .filter(gf_id=gf_id)
            return filtered
        return TblAfHatGf.objects.all()


class TblGfHatTfViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblGfHatTfSerializer

    def get_queryset(self):
        if 'gf_id' in self.request.GET and 'tf_id' in self.request.GET:
            gf_id = self.request.GET['gf_id']
            tf_id = self.request.GET['tf_id']
            filtered = TblGfHatTf.objects.filter(gf_id=gf_id) \
                .filter(tf_id=tf_id)
            return filtered
        return TblGfHatTf.objects.all()


class TblTfHatSchreibweiseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblTfHatSchreibweiseSerializer

    def get_queryset(self):
        if 'tf_id' in self.request.GET and 'schreibweise_id' in self.request.GET:
            tf_id = self.request.GET['tf_id']
            schreibweise_id = self.request.GET['schreibweise_id']
            filtered = TblTfHatSchreibweise.objects.filter(tf_id=tf_id) \
                .filter(schreibweise_id=schreibweise_id)
            return filtered
        return TblTfHatSchreibweise.objects.all()


class TblAppliedRolleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAppliedRolleSerializer

    def get_queryset(self):
        if 'rollenid' in self.request.GET and 'user_id_name_combi' in self.request.GET:
            rollenid = self.request.GET['rollenid']
            user_id_name_combi = self.request.GET['user_id_name_combi']
            filtered = TblAppliedRolle.objects.filter(model_rolle_id=rollenid).filter(
                userHatUserID_id=user_id_name_combi)
            return filtered
        return TblAppliedRolle.objects.all()

    def create(self, request, *args, **kwargs):
        print("In AppliedRoleViewSet-Create")
        serializer = TblAppliedRolleSerializer(data=request.data)
        if serializer.is_valid():
            applied_rolle = serializer.save()
            return Response(data=TblAppliedRolleSerializer(applied_rolle, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        print("In AppliedRoleViewSet-Patch")
        if 'bulk-delete' in request.POST:
            filtered = TblAppliedRolle.objects.filter(userHatUserID_id=request.POST['userid'])
            for applied_tf in filtered:
                applied_tf.delete()
            return Response(status=status.HTTP_200_OK)
        pk = request.POST['applied_rolle_id']
        applied_rolle_to_update = TblAppliedRolle.objects.get(id=pk)
        update_afs = applied_rolle_to_update.applied_afs
        update_afs.add(request.POST['applied_af_id'])
        return Response(status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        print("In AppliedRoleViewSet-POST")
        return


class TblAppliedAfsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAppliedAfSerializer

    def get_queryset(self):
        if 'af_id' in self.request.GET and 'user_id_name_combi' in self.request.GET and 'applied_rolle_id' in self.request.GET:
            af_id = self.request.GET['af_id']
            user_id_name_combi = self.request.GET['user_id_name_combi']
            applied_rolle_id = self.request.GET['applied_rolle_id']

            filtered = TblAppliedAf.objects.filter(model_af_id=af_id) \
                .filter(userHatUserID_id=user_id_name_combi).filter(applied_rolle_id=applied_rolle_id)
            return filtered
        return TblAppliedAf.objects.all()

    def create(self, request, *args, **kwargs):
        print("In AppliedAfViewSet-Create")
        serializer = TblAppliedAfSerializer(data=request.data)
        if serializer.is_valid():
            applied_af = serializer.save()
            return Response(data=TblAppliedAfSerializer(applied_af, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        print("In AppliedAfViewSet-Patch")
        if 'bulk-delete' in request.POST:
            filtered = TblAppliedAf.objects.filter(userHatUserID_id=request.POST['userid'])
            for applied_tf in filtered:
                applied_tf.delete()
            return Response(status=status.HTTP_200_OK)
        pk = request.POST['applied_af_id']
        applied_af_to_update = TblAppliedAf.objects.get(id=pk)
        update_gfs = applied_af_to_update.applied_gfs
        update_gfs.add(request.POST['applied_gf_id'])
        return Response(status=status.HTTP_201_CREATED)


class TblAppliedGfsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAppliedGfSerializer

    def get_queryset(self):
        if 'gf_id' in self.request.GET and 'user_id_name_combi' in self.request.GET \
                and 'applied_af_id' in self.request.GET and 'applied_rolle_id' in self.request.GET:
            gf_id = self.request.GET['gf_id']
            user_id_name_combi = self.request.GET['user_id_name_combi']
            applied_rolle_id = self.request.GET['applied_rolle_id']
            applied_af_id = self.request.GET['applied_af_id']

            filtered = TblAppliedGf.objects.filter(model_gf_id=gf_id) \
                .filter(userHatUserID_id=user_id_name_combi) \
                .filter(applied_rolle_id=applied_rolle_id) \
                .filter(applied_af_id=applied_af_id)
            return filtered
        return TblAppliedGf.objects.all()

    def create(self, request, *args, **kwargs):
        print("In AppliedGfViewSet-Create")
        serializer = TblAppliedGfSerializer(data=request.data)
        if serializer.is_valid():
            applied_gf = serializer.save()
            return Response(data=TblAppliedGfSerializer(applied_gf, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        print("In AppliedGfViewSet-Patch")
        if 'bulk-delete' in request.POST:
            filtered = TblAppliedGf.objects.filter(userHatUserID_id=request.POST['userid'])
            for applied_tf in filtered:
                applied_tf.delete()
            return Response(status=status.HTTP_200_OK)
        pk = request.POST['applied_gf_id']
        applied_gf_to_update = TblAppliedGf.objects.get(id=pk)
        update_tfs = applied_gf_to_update.applied_tfs
        update_tfs.add(request.POST['applied_tf_id'])
        return Response(status=status.HTTP_201_CREATED)


class TblAppliedTfsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TblAppliedTfSerializer

    def get_queryset(self):
        if 'tf_id' in self.request.GET and 'user_id_name_combi' in self.request.GET \
                and 'applied_af_id' in self.request.GET \
                and 'applied_gf_id' in self.request.GET and 'applied_rolle_id' in self.request.GET:
            tf_id = self.request.GET['tf_id']
            user_id_name_combi = self.request.GET['user_id_name_combi']
            applied_rolle_id = self.request.GET['applied_rolle_id']
            applied_af_id = self.request.GET['applied_af_id']
            applied_gf_id = self.request.GET['applied_gf_id']

            filtered = TblAppliedTf.objects.filter(model_tf_id=tf_id) \
                .filter(userHatUserID_id=user_id_name_combi) \
                .filter(applied_rolle_id=applied_rolle_id) \
                .filter(applied_af_id=applied_af_id) \
                .filter(applied_gf_id=applied_gf_id)
            return filtered
        return TblAppliedTf.objects.all()

    def create(self, request, *args, **kwargs):
        print("In AppliedTfViewSet-Create")
        serializer = TblAppliedTfSerializer(data=request.data)
        if serializer.is_valid():
            applied_tf = serializer.save()
            return Response(data=TblAppliedTfSerializer(applied_tf, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        print("In AppliedTfViewSet-Patch")
        if 'bulk-delete' in request.POST:
            filtered = TblAppliedTf.objects.filter(userHatUserID_id=request.POST['userid'])
            for applied_tf in filtered:
                applied_tf.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OnePerPagePagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1


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


class FullTblRollenViewSet(TblRollenViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullTblRollenSerializer


class FullTblAflisteViewSet(TblAflisteViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullTblAflisteSerializer


class FullTblUebersichtAfGfsViewSet(TblUebersichtAfGfsViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullTblUebersichtAFGfsSerializer


class FullTblTfsViewSet(TblTfViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullTblTfsSerializer


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



# Create your views here.
'''
