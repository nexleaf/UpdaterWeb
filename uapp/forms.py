from crispy_forms.helper import FormHelper
from django import forms
from uapp.choices import *
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div

class UserForm(forms.Form):
	
	imei = forms.CharField(label='imei', max_length=100)
	group = forms.ChoiceField(label="group",choices = CHOICES,)
	inventory_info = forms.MultipleChoiceField(
        choices = (
            ('option_one', "Lock Inventory Information"), 
            ),
        widget = forms.CheckboxInput,
    )
	sim_id = forms.CharField(label='Sim ID', max_length=100)
	phone_number = forms.CharField(label='Phone Number', max_length=100)
	asset_tag = forms.CharField(label='Asset tag', max_length=100)
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
	

