from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from pyano2.models import Invitation, Survey
from django.utils.translation import ugettext_lazy as _


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text=_('First name.'))
    last_name = forms.CharField(max_length=30, required=False, help_text=_('Last name.'))
    email = forms.EmailField(max_length=254, help_text=_('Required. Inform a valid email address.'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


JOB_CHOICES = (
    (1, _("Reviewer")),
    (2, _("Annotator"))
)


class InviteReviewerAnnotatorForm(forms.Form):
    surveys = Survey.objects.filter(is_published=True)
    SURVEY_CHOICES = []
    for survey in surveys:
        SURVEY_CHOICES.append((survey.id, survey.name))
    SURVEY_CHOICES = tuple(SURVEY_CHOICES)
    name = forms.CharField(max_length=255, label="Target name", help_text=_("Full name"))
    job = forms.ChoiceField(label="Position to invite", choices=JOB_CHOICES, initial='', widget=forms.Select(), required=True)
    email = forms.EmailField(max_length=254, help_text=_('Required. Inform a valid email address.'))
    survey = forms.ChoiceField(label='Work to do', choices=SURVEY_CHOICES, initial='', widget=forms.Select(), required=True, help_text=_('Name of the surveys'))
    class Meta:
        model = Invitation
        fields = ('name', 'job', 'email', 'survey')



class SearchForm(forms.Form):
    topic = forms.HiddenInput()
    keywords = forms.CharField(max_length=255, label="Keywords")
    hd = forms.CheckboxInput(attrs={'title': 'HD videos only.'})
    cc = forms.CheckboxInput(attrs={'title': 'CreativeCommons videos only.'})
    long_videos = forms.CheckboxInput(attrs={'title': 'Long videos only.'})
