from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_bootstrap5.bootstrap5 import FloatingField
from django import forms
from .models import FreightRoute

class StandardFreightCalculatorForm(forms.Form):
    route = forms.ModelChoiceField(queryset=FreightRoute.objects.filter(type='standard'), label='Route')
    m3 = forms.ChoiceField(choices=[('small', '12,500'), ('medium', '60,000'), ('large', '335,000')], label='Contract Size (m3)')
    collateral = forms.CharField(label='Collateral (e.g 1.4b)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'standard'
        self.helper.layout = Layout(
            FloatingField('route'),
            FloatingField('m3'),
            FloatingField('collateral'),
        )

        self.helper.add_input(Submit('submit', 'Submit'))

class WormholeCalculatorForm(forms.Form):
    route = forms.ModelChoiceField(queryset=FreightRoute.objects.filter(type='wormhole'), label='Route')
    m3 = forms.ChoiceField(choices=[('small', '12,500'), ('medium', '60,000')], label='Contract Size (m3)')
    collateral = forms.CharField(label='Collateral (e.g 1.4b)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'wormhole'
        self.helper.layout = Layout(
            FloatingField('route'),
            FloatingField('m3'),
            FloatingField('collateral'),
        )

        self.helper.add_input(Submit('submit', 'Submit'))