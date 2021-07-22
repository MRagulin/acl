from django import forms

class email_form(forms.Form):
    """Форма для тестовых сообщений"""
    email = forms.CharField(max_length=32)
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 20}))