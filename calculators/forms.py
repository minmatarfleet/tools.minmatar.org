from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_bootstrap5.bootstrap5 import FloatingField
from django import forms
from .models import FreightRoute

class FreightCalculatorForm(forms.Form):
    route = forms.ModelChoiceField(queryset=FreightRoute.objects.all(), label='Route')
    m3 = forms.CharField(label='Contract Size (m3), max 335,000')
    collateral = forms.CharField(label='Collateral (e.g 1.4b)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'freight-calculator'
        self.helper.layout = Layout(
            FloatingField('route'),
            FloatingField('m3'),
            FloatingField('collateral'),
        )

        self.helper.add_input(Submit('submit', 'Submit'))

class StandardFreightCalculatorForm(forms.Form):
    route = forms.ModelChoiceField(queryset=FreightRoute.objects.filter(jump_freight_only=False), label='Route')
    m3 = forms.ChoiceField(choices=[('12500', '12,500'), ('60000', '60,000')], label='Contract Size (m3)')
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

class JumpFreightCalculatorForm(forms.Form):
    route = forms.ModelChoiceField(queryset=FreightRoute.objects.filter(jump_freight_capable=True), label='Route')
    m3 = forms.ChoiceField(choices=[('60000', '60,000'), ('335000', '335,000')], label='Contract Size (m3)')
    collateral = forms.CharField(label='Collateral (e.g 1.4b)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'jump'
        self.helper.layout = Layout(
            FloatingField('route'),
            FloatingField('m3'),
            FloatingField('collateral'),
        )

        self.helper.add_input(Submit('submit', 'Submit'))