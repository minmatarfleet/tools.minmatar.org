from django import forms
from django.urls import reverse
from .models import EveContractEntityManager, EveContractExpectation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

class EveContractEntityForm(forms.Form):
    entity_id = forms.IntegerField(widget=forms.HiddenInput)
    entity_name = forms.CharField(max_length=255, widget=forms.HiddenInput)
    type = forms.ChoiceField(choices=(('character', 'Character'), ('corporation', 'Corporation')), widget=forms.HiddenInput)
    contact_character_name = forms.CharField(max_length=255, help_text='The contract character for this entity, such as your main character.')
    contact_character_id = forms.IntegerField(help_text='Character ID for contract character, can pull from zKill https://zkillboard.com/character/211200')
    contact_discord_name = forms.CharField(max_length=255, help_text='The discord name of the user, not the id. (e.g BearThatCares#1337)')
    contact_discord_id = forms.IntegerField(help_text='The discord id of the user, not the name. This can be found by right clicking on the user and selecting "Copy ID" with developer mode on.')
    ceo_id = forms.IntegerField(required=False, widget=forms.HiddenInput, help_text='The character ID of the CEO of the corporation')
    challenge = forms.CharField(max_length=36, widget=forms.HiddenInput, help_text='The challenge code for the entity, this is used to verify the entity is who they say they are. DO NOT TOUCH.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'submit-contract-entity'
        self.helper.add_input(Submit('submit', 'Submit'))

class EveContractEntityReponsibilityForm(forms.Form):
    expectation = forms.ModelChoiceField(queryset=EveContractExpectation.objects.all(), help_text='The contract you would like to support')
    challenge = forms.CharField(max_length=36, widget=forms.HiddenInput, help_text='Challenge code for the entity')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'submit-contract-entity-responsibility'
        self.helper.form_class = 'row row-cols-lg-auto'
        self.helper.label_class = 'visually-hidden'
        self.helper.add_input(Submit('submit', 'Add responsibility', wrapper_class="col-12"))
        self.helper.layout = Layout(
            Field('expectation', wrapper_class='col-12'),
            Field('challenge'),
        )

class EveContractEntityManagerForm(forms.ModelForm):
    challenge = forms.CharField(max_length=36, widget=forms.HiddenInput, help_text='Challenge code for the entity')

    class Meta:
        model = EveContractEntityManager
        fields = ['character_id']
        help_texts = {
            'character_id': 'Character ID of the manager'
        }

    def __init__(self, *args, **kwargs):
        super(EveContractEntityManagerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = 'submit-contract-entity-manager'
        self.helper.form_class = 'row row-cols-lg-auto'
        self.helper.label_class = 'visually-hidden'
        self.helper.add_input(Submit('submit', 'Add manager'))
        self.helper.layout = Layout(
            Field('character_id', wrapper_class='col-12'),
            Field('challenge'),
        )
