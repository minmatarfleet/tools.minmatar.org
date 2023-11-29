from django.urls import reverse
from esi.decorators import token_required, tokens_required
from django.shortcuts import render, redirect
from .forms import EveContractEntityForm, EveContractEntityReponsibilityForm, EveContractEntityManagerForm
from .models import EveContractEntity, EveContractEntityCodeChallenge, EveContractEntityManager, EveContractExpectation, EveDoctrineExpectation
from esi.clients import EsiClientProvider
from django.contrib.auth.decorators import login_required
import uuid
from .helpers import get_bucketed_fittings_sales, get_items_sales, get_entity_taxes, get_ship_sales
from pydantic import BaseModel
from django.http import JsonResponse
from typing import Any
from .helpers import get_entity_total_sales
from django.views.decorators.cache import cache_page
from contracts_v2.modules.history import get_contract_historical_summary
from contracts_v2.modules.status import get_contract_summary, get_contract_summary_by_fittings


esi = EsiClientProvider()

# Create your views here.
@login_required()
def public_contract_list(request):
    entities = EveContractEntity.objects.all()
    expectations = EveContractExpectation.objects.filter(active=True)
    contract_summary = get_contract_summary(expectations)
    contract_historical_summary = get_contract_historical_summary([e.fitting for e in expectations])
    
    context = {
        'entities': entities,
        'contract_summary': contract_summary,
        'historical_contract_summary': contract_historical_summary,
    }

    return render(request, 'contracts_v2/public_contract_list.html', context)

def public_doctrine_contract_list(request):
    entities = EveContractEntity.objects.filter(domain="Public Doctrine Seeding")
    expectations = EveDoctrineExpectation.objects.filter(type="public")
    fittings = []
    for expectation in expectations:
        doctrine_fittings = expectation.doctrine.fittings.all()
        for fitting in doctrine_fittings:
            fittings.append(fitting)

    current_summary = get_contract_summary_by_fittings(fittings, alliance=False)
    historical_summary = get_contract_historical_summary(fittings)

    context = {
        'entities': entities,
        'expectations': expectations,
        'contract_summary': current_summary,
        'historical_contract_summary': historical_summary,
    }

    return render(request, 'contracts_v2/public_doctrine_contract_list.html', context)

def alliance_doctrine_contract_list(request):
    entities = EveContractEntity.objects.filter(domain="Alliance Doctrine Seeding")
    expectations = EveDoctrineExpectation.objects.filter(type="alliance")
    fittings = []
    for expectation in expectations:
        doctrine_fittings = expectation.doctrine.fittings.all()
        for fitting in doctrine_fittings:
            fittings.append(fitting)
        
    current_summary = get_contract_summary_by_fittings(fittings)
    historical_summary = get_contract_historical_summary(fittings)

    context = {
        'entities': entities,
        'expectations': expectations,
        'contract_summary': current_summary,
        'historical_contract_summary': historical_summary,
    }

    return render(request, 'contracts_v2/alliance_doctrine_contract_list.html', context)

def contract_entities_json(request):
    contract_entities = EveContractEntity.objects.all()
    reponse = []
    for contract_entity in contract_entities:
        reponse.append({
            'Name': contract_entity.entity_name,
            'Type': contract_entity.type,
            'Discord Contact' : contract_entity.contact_discord_name,
        })
    return JsonResponse(reponse, safe=False)

@token_required(scopes=['esi-contracts.read_character_contracts.v1'])
def create_contract_character_entity(request, token):
    EveContractEntityCodeChallenge.objects.create(entity_id=token.character_id, entity_name=token.character_name, type="character", challenge=str(uuid.uuid4()))
    form = EveContractEntityForm(
        initial={
            'entity_id': token.character_id,
            'entity_name': token.character_name,
            'type': 'character',
            'contact_character_id': token.character_id,
            'contact_character_name': token.character_name,
            'challenge': EveContractEntityCodeChallenge.objects.filter(entity_id=token.character_id).first().challenge,
        }
    )

    return render(request, 'contracts_v2/create_contract_entity.html', {'form': form})

@login_required
@token_required(scopes=['esi-contracts.read_corporation_contracts.v1'])
def create_contract_corporation_entity(request, token):
    character_information = esi.client.Character.get_characters_character_id(character_id=token.character_id).result()
    corporation_id = character_information['corporation_id']
    corporation_information = esi.client.Corporation.get_corporations_corporation_id(corporation_id=corporation_id).result()

    if token.character_id != corporation_information['ceo_id']:
        return render(request, 'contracts_v2/create_contract_entity.html', {'error': "You are not the CEO of this corporation."})

    EveContractEntityCodeChallenge.objects.create(entity_id=corporation_id, entity_name=corporation_information['name'], type="corporation", challenge=str(uuid.uuid4()))
    form = EveContractEntityForm(
        initial={
            'entity_id': corporation_id,
            'entity_name': corporation_information['name'],
            'type': 'corporation',
            'ceo_id': corporation_information['ceo_id'],
            'contact_character_id': token.character_id,
            'contact_character_name': token.character_name,
            'challenge': EveContractEntityCodeChallenge.objects.filter(entity_id=corporation_id).first().challenge,
        }
    )
    return render(request, 'contracts_v2/create_contract_entity.html', {'form': form})

@token_required(scopes=['esi-contracts.read_corporation_contracts.v1'], new=True)
def refresh_contract_corporation_entity_token(request, token, entity_id):
    return redirect(reverse('contract-entity-settings', kwargs={"entity_id": entity_id}))

def submit_contract_entity(request):
    if request.method == 'POST':
        form = EveContractEntityForm(request.POST)
        if form.is_valid():
            if not EveContractEntityCodeChallenge.objects.filter(entity_id=form.cleaned_data['entity_id'],
                                                                 entity_name=form.cleaned_data['entity_name'],
                                                                 type=form.cleaned_data['type'],
                                                                 challenge=form.cleaned_data['challenge']).exists():
                form.add_error('challenge', 'Challenge code is invalid')
                return render(request, 'contracts_v2/create_contract_entity.html', {'form': form})

            entity = EveContractEntity(
                entity_id=form.cleaned_data['entity_id'],
                entity_name=form.cleaned_data['entity_name'],
                type=form.cleaned_data['type'],
                ceo_id=form.cleaned_data['ceo_id'],
                contact_character_id=form.cleaned_data['contact_character_id'],
                contact_character_name=form.cleaned_data['contact_character_name'],
                contact_discord_name=form.cleaned_data['contact_discord_name'],
                contact_discord_id=form.cleaned_data['contact_discord_id'],
            )
            entity.save()
        else:
            return render(request, 'contracts_v2/create_contract_entity.html', {'form': form})
    return redirect(reverse('public-contract-list'))

@login_required()
def settings(request, entity_id):
    entity = EveContractEntity.objects.get(entity_id=entity_id)
    token = request.user.eve_character
    if not request.user.is_superuser:
        if token.character_id != entity.contact_character_id and token.character_name != entity.contact_character_name and not EveContractEntityManager.objects.filter(entity=entity, character_id=token.character_id).exists():
            return render(request, 'contracts_v2/settings.html', {'error': "You are not the CEO or a valid character for this entity."})
    EveContractEntityCodeChallenge.objects.create(entity_id=entity.entity_id, entity_name=entity.entity_name, type=entity.type, challenge=str(uuid.uuid4()))
    challenge = EveContractEntityCodeChallenge.objects.filter(entity_id=entity.entity_id).first().challenge
    reponsibility_form = EveContractEntityReponsibilityForm(initial={'challenge': challenge})
    manager_form = EveContractEntityManagerForm(initial={'challenge': challenge})
    responsibilities = EveContractExpectation.objects.filter(entities=entity)
    managers = EveContractEntityManager.objects.filter(entity=entity)
    context = {
        'responsibility_form': reponsibility_form,
        'manager_form': manager_form,
        'responsibilities': responsibilities,
        'managers': managers,
        'entity': entity,
    }
    return render(request, 'contracts_v2/settings.html', context)

def submit_contract_entity_reponsibility(request):
    if request.method == 'POST':
        form = EveContractEntityReponsibilityForm(request.POST)
        if form.is_valid():
            challenge = EveContractEntityCodeChallenge.objects.get(challenge=form.cleaned_data['challenge'])
            entity = EveContractEntity.objects.get(entity_id=challenge.entity_id)
            expectation = form.cleaned_data['expectation']
            expectation.entities.add(entity)

            return redirect(reverse('contract-entity-settings', kwargs={"entity_id": entity.entity_id}))

    return render(request, 'contracts_v2/submit_error.html', {'error': form.errors})

def submit_contract_entity_manager(request):
    if request.method == 'POST':
        form = EveContractEntityManagerForm(request.POST)
        if form.is_valid():
            challenge = EveContractEntityCodeChallenge.objects.get(challenge=form.cleaned_data['challenge'])
            entity = EveContractEntity.objects.get(entity_id=challenge.entity_id)
            manager = EveContractEntityManager(
                entity=entity,
                character_id=form.cleaned_data['character_id'],
            )
            manager.save()

    return redirect(reverse('contract-entity-settings', kwargs={"entity_id": entity.entity_id}))

@login_required()
def delete_contract_entity(request, entity_id):
    token = request.user.eve_character
    entity = EveContractEntity.objects.get(entity_id=entity_id)
    if token.character_id != entity.contact_character_id and token.character_name != entity.contact_character_name and not EveContractEntityManager.objects.filter(entity=entity, character_id=token.character_id).exists():
        return render(request, 'contracts_v2/settings.html', {'error': "You are not the CEO or a valid character for this entity."})
    entity.delete()
    return redirect("public-contract-list")

@login_required()
def delete_contract_entity_responsbility(request, entity_id, expectation_id):
    token = request.user.eve_character
    expectation = EveContractExpectation.objects.get(id=expectation_id)
    entity = EveContractEntity.objects.get(entity_id=entity_id)
    if token.character_id != entity.contact_character_id and token.character_name != entity.contact_character_name and not EveContractEntityManager.objects.filter(entity=entity, character_id=token.character_id).exists():
        return render(request, 'contracts_v2/settings.html', {'error': "You are not the CEO or a valid character for this entity."})
    expectation.entities.remove(entity)
    return redirect("contract-entity-settings" + str(entity.entity_id))

@login_required()
def delete_contract_entity_manager(request, manager_id):
    token = request.user.eve_character
    manager = EveContractEntityManager.objects.get(id=manager_id)
    if token.character_id != manager.entity.contact_character_id and token.character_name != manager.entity.contact_character_name and not EveContractEntityManager.objects.filter(entity=manager.entity, character_id=token.character_id).exists():
        return render(request, 'contracts_v2/settings.html', {'error': "You are not the CEO or a valid character for this entity."})
    manager.delete()
    return redirect("public-contract-list")

@cache_page(60 * 15)
def statistics_json(request):
    data = get_entity_total_sales()
    return JsonResponse(data, safe=False)

class ContractEntityTaxResponse(BaseModel):
    entity_name: str
    estimated_sales: float
    estimated_tax: int
    total_estimated_sales: float = 0
    total_estimated_tax: int = 0

@cache_page(60 * 60 * 4)
def taxes(request):
    contract_entity_tax_responses, total_estimated_sales, total_estimated_tax = get_entity_taxes()
    return render(request, 'contracts_v2/taxes.html', {'data': contract_entity_tax_responses, 'total_estimated_sales': total_estimated_sales, 'total_estimated_tax': total_estimated_tax})

@cache_page(60 * 60 * 4)
def sales_fittings(request):
    sales = sorted(get_bucketed_fittings_sales(), key=lambda x: x["sales"]["total"], reverse=True)
    context = {
        "type": "Fitting",
        "json_route": "contract-sales-fittings-json",
        "sales": sales
    }
    return render(request, 'contracts_v2/sales_fittings.html', context)

@cache_page(60 * 60 * 4)
def sales_ships(request):
    sales = [v | {"ship_name": k} for k, v in get_ship_sales().items()]
    sales = sorted(sales, key=lambda x: x["total"], reverse=True)
    context = {
        "type": "Ship",
        "json_route": "contract-sales-ships-json",
        "sales": sales
    }
    return render(request, 'contracts_v2/sales_ships.html', context)

@cache_page(60 * 60 * 4)
def sales_items(request):
    sales = sorted(get_items_sales().items(), key=lambda x: x[1]["total"], reverse=True)
    context = {
        "type": "Item",
        "json_route": "contract-sales-items-json",
        "sales": sales
    }
    return render(request, 'contracts_v2/sales_items.html', context)

@cache_page(60 * 60 * 4) 
def sales_fittings_json(_request):
    sales = {s["fitting"].name: s["sales"] for s in get_bucketed_fittings_sales()}
    return JsonResponse(sales)

@cache_page(60 * 60 * 4)
def sales_ships_json(_request):
    return JsonResponse(get_ship_sales())

@cache_page(60 * 60 * 4)
def sales_items_json(_request):
    return JsonResponse(get_items_sales())
