from django import forms


class SearchForm(forms.Form):
    topic = forms.HiddenInput()
    keywords = forms.CharField(max_length=255, label="Keywords")
    hd = forms.CheckboxInput(attrs={'title': 'HD videos only.'})
    cc = forms.CheckboxInput(attrs={'title': 'CreativeCommons videos only.'})
    long_videos = forms.CheckboxInput(attrs={'title': 'Long videos only.'})
