from django import forms
from django.core import validators

class ReaderFilter(forms.Form):
    filter_list = (('firstname', 'Author Firstname'), ('lastname', 'Author Lastname'), ('title', 'Book Title'), ('isbn', 'ISBN'), ('status', 'Books availability (available, lended)'))
    filter_key = forms.ChoiceField(choices=filter_list)
    search_key = forms.CharField()
    botcatcher = forms.CharField(required = False,
                                widget = forms.HiddenInput,
                                validators = [validators.MaxLengthValidator(0)])