from crispy_forms.helper import FormHelper
from django import forms
# from uapp.choices import *
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div
from uapp.models import Group


def get_group_choices():
        g= Group.objects.all()
        CHOICES = ()
        # l=1
        for i in g:
          CHOICES = CHOICES + ((i.name,i.name,),)
          # l=l+1
        return CHOICES

class UserForm(forms.Form):
    print "lol"

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['user_group'] = forms.ChoiceField(
            label="group",choices=get_group_choices() )
    user_imei = forms.CharField(label='imei', max_length=100)
    user_group = forms.ChoiceField(label="group",choices = get_group_choices(),)
    sim_id = forms.CharField(label='Sim ID', max_length=100)
    phone = forms.CharField(label='Phone Number', max_length=100)
    jitter = forms.IntegerField(label='Jitter')
    
    helper = FormHelper()

class GroupForm(forms.Form):
    group = forms.CharField(label='Name', max_length=100)
    desc = forms.CharField(label='Description', max_length=100)
    jitter = forms.IntegerField(label='Jitter')

class ApplicationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['app_group'] = forms.ChoiceField(
            label="group",choices=get_group_choices() )

    app_name = forms.CharField(label='Name', max_length=100)
    release = forms.CharField(label='Release', max_length=100)
    version = forms.IntegerField(label='Version')
    app_group = forms.ChoiceField(label="group",choices = get_group_choices(),)
    package = forms.CharField(label='Package', max_length=100)
    url = forms.CharField(label='URL', max_length=100)
    action = forms.CharField(label='Action', max_length=100)
    extra_urls = forms.CharField(label='Extra URLs', max_length=200)

class ReleaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)
        self.fields['app_group'] = forms.ChoiceField(
            label="group",choices=get_group_choices() )

    release = forms.CharField(label='Release', max_length=100)
    version = forms.IntegerField(label='Version')
    app_group = forms.ChoiceField(label="group",choices = get_group_choices(),)

    package = forms.CharField(label='Package', max_length=100)
    url = forms.CharField(label='URL', max_length=100)
    action = forms.CharField(label='Action', max_length=100)

class VersionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(VersionForm, self).__init__(*args, **kwargs)
        self.fields['app_group'] = forms.ChoiceField(
            label="group",choices=get_group_choices() )

    version = forms.IntegerField(label='Version')
    app_group = forms.ChoiceField(label="group",choices = get_group_choices(),)

    package = forms.CharField(label='Package', max_length=100)
    url = forms.CharField(label='URL', max_length=100)
    action = forms.CharField(label='Action', max_length=100)

class GroupEditForm(forms.Form):
    group = forms.CharField(label='Name', max_length=100)
    desc = forms.CharField(label='Description', max_length=100)
