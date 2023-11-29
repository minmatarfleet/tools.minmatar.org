from datetime import datetime, timedelta, timezone

from fleets import eft
from .models import EsiEntityContractResponse, EveContractEntity, EveContractLocation, EveContractExpectation
from fleets.models import EveFitting
import json 
from pydantic import BaseModel
from dateutil.parser import isoparse

station_id = 60004600
station_name = "Auga X - Moon 3 - Brutor Tribe Bureau"

def get_expectation_aliases():
    aliases = []
    for expectation in EveContractExpectation.objects.all():
        if expectation.aliases:
            for alias in expectation.aliases.split(','):
                aliases.append(alias)
    legacy_aliases = [expectation.legacy_alias for expectation in EveContractExpectation.objects.all()]
    return aliases, legacy_aliases

def get_entity_total_sales():
    total_sales_response = {}
    location_ids = EveContractLocation.objects.values_list('location_id', flat=True)
    aliases, legacy_aliases = get_expectation_aliases()
    fittings = [expectation.fitting for expectation in EveContractExpectation.objects.all()]
    ship_names = set([fitting.ship_name for fitting in fittings])
    for entity in EveContractEntity.objects.filter(active=True):
        print("Processing {}".format(entity.entity_name))
        total_sales = 0.0
        # fetch response based charater_id or corporation_id
        response = EsiEntityContractResponse.objects.filter(entity=entity).first() 
        if not response:
            print("No response for {}, skipping".format(entity.entity_name))
            continue
        data = json.loads(response.data)
        entity_ship_sales_data = {}
        entity_ship_outstanding_data = {}
        improperly_named_contracts = set()
        for contract in data:
            if contract['type'] == 'item_exchange' and contract['status'] == 'finished' and contract['start_location_id'] in location_ids and (contract['issuer_id'] == entity.entity_id or (contract['for_corporation'] and contract['issuer_corporation_id'] == entity.entity_id)):
                valid = False 
                contract_ship_name = None
                # skip if any ship_name is in the contract title
                for ship_name in ship_names:
                    if ship_name in contract['title']:
                        valid = True 
                        contract_ship_name = ship_name

                # check if any fitting name is in the contract title
                for fitting in fittings:
                    if fitting.name in contract['title']:
                        valid = True
                        contract_ship_name = fitting.ship_name

                # check if any expectation alias is in the contract title
                for alias in legacy_aliases:
                    if alias and alias in contract['title']:
                        valid = True 
                        expectation = EveContractExpectation.objects.get(legacy_alias=alias)
                        contract_ship_name = expectation.fitting.ship_name

                # check if any alias is in the contract title
                for alias in aliases:
                    if alias and alias in contract['title']:
                        valid = True 
                        expectation = EveContractExpectation.objects.get(aliases__contains=alias)
                        contract_ship_name = expectation.fitting.ship_name

                if not valid:
                    print("Contract {} is not valid".format(contract['title']))
                    improperly_named_contracts.add(contract['title'])
                    continue

                if contract_ship_name not in entity_ship_sales_data:
                    entity_ship_sales_data[contract_ship_name] = {
                        'quantity': 0,
                        'revenue': 0.0,
                    }

                # remove empty string from improperly_named_contracts
                improperly_named_contracts.discard('')
                entity_ship_sales_data[contract_ship_name]['quantity'] += 1
                entity_ship_sales_data[contract_ship_name]['revenue'] += contract['price']
                total_sales += contract['price']

            elif contract['type'] == 'item_exchange' and contract['status'] == 'outstanding' and contract['start_location_id'] in location_ids and (contract['issuer_id'] == entity.entity_id or (contract['for_corporation'] and contract['issuer_corporation_id'] == entity.entity_id)):
                valid = False 
                contract_ship_name = None 
                # skip if any ship_name is in the contract title
                for ship_name in ship_names:
                    if ship_name in contract['title']:
                        valid = True 
                        contract_ship_name = ship_name

                # check if any fitting name is in the contract title
                for fitting in fittings:
                    if fitting.name in contract['title']:
                        valid = True
                        contract_ship_name = fitting.ship_name

                # check if any expectation alias is in the contract title
                for alias in legacy_aliases:
                    if alias and alias in contract['title']:
                        valid = True 
                        expectation = EveContractExpectation.objects.get(legacy_alias=alias)
                        contract_ship_name = expectation.fitting.ship_name

                # check if any alias is in the contract title
                for alias in aliases:
                    if alias and alias in contract['title']:
                        valid = True 
                        expectation = EveContractExpectation.objects.get(aliases__contains=alias)
                        contract_ship_name = expectation.fitting.ship_name

                if not valid:
                    print("Contract {} is not valid".format(contract['title']))
                    improperly_named_contracts.add(contract['title'])
                    continue

                if contract_ship_name not in entity_ship_outstanding_data:
                    entity_ship_outstanding_data[contract_ship_name] = {
                        'quantity': 0,
                        'revenue': 0.0,
                    }

                # remove empty string from improperly_named_contracts
                improperly_named_contracts.discard('')
                entity_ship_outstanding_data[contract_ship_name]['quantity'] += 1
                entity_ship_outstanding_data[contract_ship_name]['revenue'] += contract['price']

        total_sales_response[entity.entity_name] = {
            'total_sales': total_sales,
            'outstanding_contracts': entity_ship_outstanding_data,
            'ship_sales': entity_ship_sales_data,
            'improperly_named_contracts': list(improperly_named_contracts)
        }

    # dump json to file
    return total_sales_response

def get_fitting_sales():
    location_ids = EveContractLocation.objects.values_list('location_id', flat=True)
    aliases, legacy_aliases = get_expectation_aliases()
    fittings = [expectation.fitting for expectation in EveContractExpectation.objects.all()]

    fittings_sales = {}
    for entity in EveContractEntity.objects.all():
        response = EsiEntityContractResponse.objects.filter(entity=entity).first() 
        if not response:
            print("No response for {}, skipping".format(entity.entity_name))
            continue
        data = json.loads(response.data)
        for contract in data:
            if contract['type'] == 'item_exchange' and contract['status'] == 'finished' and contract['start_location_id'] in location_ids:
                contract_fitting = None
                for fitting in fittings:
                    if fitting.name in contract['title']:
                        contract_fitting = fitting

                for alias in legacy_aliases:
                    if alias and alias in contract['title']:
                        expectation = EveContractExpectation.objects.get(legacy_alias=alias)
                        contract_fitting = expectation.fitting

                for alias in aliases:
                    if alias and alias in contract['title']:
                        expectation = EveContractExpectation.objects.get(aliases__contains=alias)
                        contract_fitting = expectation.fitting
                if contract_fitting:
                    fittings_sales.setdefault(contract_fitting.id, {"fitting": contract_fitting, "sales": []})["sales"].append(contract['date_completed'])
    return fittings_sales.values()

def get_bucketed_fittings_sales():
    fittings_sales = get_fitting_sales()
    for fitting_sales in fittings_sales:
        fitting_sales["sales"] = bucket_sales((ts, 1) for ts in fitting_sales["sales"])
    return fittings_sales

def get_ship_sales():
    def sum_sales(a, b):
        return {
            "total": a["total"] + b["total"],
            "weeks": [
                a["weeks"][0] + b["weeks"][0],
                a["weeks"][0] + b["weeks"][1],
                a["weeks"][0] + b["weeks"][2],
                a["weeks"][0] + b["weeks"][3],
            ]
        }
    sales = {}
    for fs in get_bucketed_fittings_sales():
        ship_name = fs["fitting"].ship_name
        s = sales.setdefault(ship_name, {"total": 0, "weeks": [0, 0, 0, 0]})
        sales[ship_name] = sum_sales(s, fs["sales"])
    return sales

def get_items_sales():
    fittings_sales = get_fitting_sales()
    items_sales = {}
    for fitting_sales in fittings_sales:
        fit = eft.parse_eft(fitting_sales["fitting"].eft_format)
        for sale_timestamp in fitting_sales["sales"]:
            for _, items in fit.sections():
                for item in items:
                    items_sales.setdefault(item.name, []).append((sale_timestamp, int(item.amount)))
    for item, sales in items_sales.items():
        items_sales[item] = bucket_sales(sales)
    return items_sales

def bucket_sales(sales: list[(datetime, int)]):
    sales = [(isoparse(ts), amount) for ts, amount in sales]
    total = sum(s[1] for s in sales)
    now = datetime.now(timezone.utc)
    weeks = []
    for w in [1, 2, 3, 4]:
        t0 = now - timedelta(weeks=w)
        t1 = now - timedelta(weeks=w-1)
        weeks.append(sum(amount for (ts, amount) in sales if t0 < ts < t1))
    return {"total": total, "weeks": weeks}

class ContractEntityTaxResponse(BaseModel):
    entity_name: str
    estimated_sales: float
    estimated_tax: int
    total_estimated_sales: float = 0
    total_estimated_tax: int = 0

def get_entity_taxes():
    tax_rate = 0.025
    data = get_entity_total_sales()
    contract_entity_tax_responses = []
    total_estimated_sales = 0
    total_estimated_tax = 0
    for entity in data:
        sales_data = data[entity]
        tax = (sales_data['total_sales'] / 1.2) * tax_rate
        contract_entity_tax_responses.append(ContractEntityTaxResponse(entity_name=entity, estimated_sales=sales_data['total_sales'], estimated_tax=tax))
        total_estimated_sales += sales_data['total_sales']
        total_estimated_tax += tax
    
    return contract_entity_tax_responses, total_estimated_sales, total_estimated_tax
