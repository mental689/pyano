from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text=_('First name.'))
    last_name = forms.CharField(max_length=30, required=False, help_text=_('Last name.'))
    email = forms.EmailField(max_length=254, help_text=_('Required. Inform a valid email address.'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class SearchForm(forms.Form):
    topic = forms.HiddenInput()
    keywords = forms.CharField(max_length=255, label="Keywords")
    hd = forms.CheckboxInput(attrs={'title': 'HD videos only.'})
    cc = forms.CheckboxInput(attrs={'title': 'CreativeCommons videos only.'})
    long_videos = forms.CheckboxInput(attrs={'title': 'Long videos only.'})
