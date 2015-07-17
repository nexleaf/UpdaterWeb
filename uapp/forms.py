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
    helper = FormHelper()

class GroupForm(forms.Form):
    group = forms.CharField(label='Name', max_length=100)
    desc = forms.CharField(label='Description', max_length=100)
    
class ApplicationForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    release = forms.CharField(label='Release', max_length=100)
    version = forms.CharField(label='Version', max_length=100)
    package = forms.CharField(label='Package', max_length=100)
    url = forms.CharField(label='URL', max_length=100)
    action = forms.CharField(label='Action', max_length=100)

class GroupEditForm(forms.Form):
    group = forms.CharField(label='Name', max_length=100)
    desc = forms.CharField(label='Description', max_length=100)
    

