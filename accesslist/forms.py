from django import forms

class Approve_form(forms.Form):
    project_name = forms.CharField(max_length=32)
    approve_person = forms.CharField(max_length=32)
    uid = forms.CharField(max_length=36)

