from datetime import datetime, timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import StructureIntel, StructureTimer
from django import forms
import re

class StructureForm(forms.Form):
    structure_name = forms.CharField(label='Structure Name', max_length=255)
    structure_type = forms.CharField(label='Structure Type', max_length=255, widget=forms.Select(choices=StructureIntel.structure_types))
    system = forms.CharField(label='System', max_length=255)
    corporation_name = forms.CharField(label='Corporation Name', max_length=255)
    alliance_name = forms.CharField(label='Alliance Name', max_length=255, required=False)
    related_alliance_name = forms.CharField(label='Related Alliance Name', max_length=255, required=False)
    timer = forms.CharField(label='Timer', max_length=5)
    fitting = forms.CharField(label='Fitting', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))


    # validate that timer is 4 digit number separated by a colon
    def clean(self):
        cleaned_data = super().clean()
        timer = cleaned_data.get("timer")

       #check timer is in format xx:xx or xxxx
        search_results = re.search("\d{2}\:?\d{2}", timer)
        if search_results is None:
            raise forms.ValidationError("Timer busy be in format HH:MM or HHMM")
        
        timer = re.sub("\:", "", timer)

        cleaned_data["timer"] = timer[0:2] + ":" + timer[2:4]
        
        return cleaned_data

class StructureTimerForm(forms.Form):
    structure_name = forms.CharField(label='Structure Name', max_length=255)
    structure_type = forms.CharField(label='Structure Type', max_length=255, widget=forms.Select(choices=StructureTimer.structure_types))
    system = forms.CharField(label='System', max_length=255)
    alliance = forms.CharField(label='Owning alliance', max_length=255)
    timer_type = forms.CharField(label='Timer Type', max_length=255, widget=forms.Select(choices=StructureTimer.timer_types))
    timer = forms.DateTimeField(label='Timer in EVE Time', widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

    def clean_timer(self):
        timer = self.cleaned_data['timer']
        if timer < datetime.now(timezone.utc):
            raise forms.ValidationError("Timer must be in the future")
        return timer

class StructureTimerPasteForm(forms.Form):
    paste = forms.CharField(label='Paste', widget=forms.Textarea(attrs={'rows': 4}))
    structure_type = forms.CharField(label='Structure Type', max_length=255, widget=forms.Select(choices=StructureTimer.structure_types))
    timer_type = forms.CharField(label='Timer Type', max_length=255, widget=forms.Select(choices=StructureTimer.timer_types))
    alliance = forms.CharField(label='Owning alliance', max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
