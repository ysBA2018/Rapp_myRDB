from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, UsernameField
from django.utils.safestring import mark_safe

from django.contrib.auth import get_user_model

#from .models import User, Orga, Group, Department, ZI_Organisation, Role, AF, GF, TF, User_AF, User_GF, User_TF, \
#    ChangeRequests
from .models import *


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ('identity',)



class CustomUserCreationForm(UserCreationForm):
    
    #    Form for password and xvNumber validation
     #   also checks if Profile has already been activated by any user by creating pswd
      #      otherwise create new
    
    class Meta:
        model = get_user_model()
        fields = ('username','email', 'first_name', 'last_name',)

    def clean(self):
        print("in clean_password2")
        cd = self.cleaned_data
        password1 = cd.get("password1")
        password2 = cd.get("password2")
        if password1 and password2 and password1 != password2:
            print("in passwords dont match")

            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return cd

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        username = self.cleaned_data['username']
        username_upper = username.upper()
        print("in save!")
        print(username, username_upper)
        try:
            user = User.objects.get(username=username)
            print("User: ", user.__str__(), " mit username_lower existiert")
            if user.password == "":
                print("User mit username_lower existiert - password is leer -> pw wird gesafet")
                user.set_password(self.cleaned_data['password1'])
                user.save()
            else:
                print("User mit username_lower existiert und hat pw!")
                forms.ValidationError("User mit username_lower existiert und hat pw!")
                return user
                # messages.info(HttpRequest(),"User exists and has a Password")
        except(KeyError, User.DoesNotExist):
            try:
                user = User.objects.get(username=username_upper)
                print("User: ", user.__str__(), " mit Identity_upper existiert")
                if user.password == "":
                    print("User mit username_upper existiert - password is leer -> pw wird gesafet")
                    user.set_password(self.cleaned_data['password1'])
                    user.save()
                else:
                    forms.ValidationError("User mit username_upper existiert und hat pw!")
                    print("User mit username_upper existiert und hat pw!")
                return user
                # messages.info(HttpRequest(),"User exists and has a Password")
            except(KeyError, User.DoesNotExist):
                print("User existiert nicht - wird neu angelegt")
                user = super(CustomUserCreationForm, self).save(commit=False)
                user.set_password(self.cleaned_data['password1'])
                username_numerics = username[2:]
                print(username_numerics)
                if commit:
                    user.save()
                    userid_names = TblUserIDundName.objects.filter(userid__endswith=username_numerics)
                    for userid_name in userid_names:
                        user.userid_name.add(userid_name.id)

        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username',)
        error_css_class = 'error'


class SomeForm(forms.Form):
    start_import = forms.FileInput()


class ApplyRightForm(forms.Form):
    reason_for_application = forms.CharField(widget=forms.Textarea(attrs={'rows': '4'}), min_length=20, max_length=500,
                                             label=mark_safe('<strong>Grund der Beantragung:</strong>'))


class DeleteRightForm(forms.Form):
    reason_for_deletion = forms.CharField(widget=forms.Textarea(attrs={'rows': '4'}), min_length=20, max_length=500,
                                          label=mark_safe('<strong>Grund der Löschung:</strong>'))


class AcceptChangeForm(forms.Form):
    change_in_IIQ_check = forms.BooleanField(label="Änderungen in IIQ beantragt?")


class DeclineChangeForm(forms.Form):
    reason_for_decline = forms.CharField(widget=forms.Textarea(attrs={'rows': '2'}), min_length=20, max_length=500,
                                         label=mark_safe('<strong>Grund der Ablehnung:</strong>'))

class ProfileHeaderForm(forms.Form):
    user_search = forms.CharField(label="",widget=forms.TextInput(attrs={'placeholder': 'vergleiche mit...'}))
