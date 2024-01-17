from datetime import datetime, timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from .models import StructureIntel, StructureTimer
from django import forms

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
        if len(timer) != 5:
            raise forms.ValidationError("Timer must be in format MM:SS")
        if timer[2] != ":":
            raise forms.ValidationError("Timer must be in format MM:SS")
        try:
            int(timer[0:2])
            int(timer[3:5])
        except ValueError:
            raise forms.ValidationError("Timer must be in format MM:SS")
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
