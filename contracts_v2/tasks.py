from tools.celery  import app 
from .models import EveContractEntity, EsiEntityContractResponse, EveContractExpectation, EveContractTaxReport, EveContract
from .helpers import get_entity_taxes
from esi.clients import EsiClientProvider
from esi.models import Token
import logging 
import datetime 
from django.utils import timezone
import json 
from discoPy.rest.client import Application, User, Guild, Channel, Stage, Webhook
from django.conf import settings
from fleets.models import EveFitting

logger = logging.getLogger(__name__)

esi = EsiClientProvider()

@app.task()
def update_esi_corporation_contract_responses():
    # Pull contracts for active entities 
    for entity in EveContractEntity.objects.all():
        try:
            if entity.type == 'corporation':
                print("updating esi corporation contract response for entity_id: {}".format(entity.entity_id))
                required_scopes = ['esi-contracts.read_corporation_contracts.v1']
                token = Token.get_token(entity.ceo_id, required_scopes)
                esi_contract_response = esi.client.Contracts.get_corporations_corporation_id_contracts(corporation_id=entity.entity_id, token=token.valid_access_token()).results()
                # save response 
                if EsiEntityContractResponse.objects.filter(entity=entity).exists():
                    esi_entity_contract_response = EsiEntityContractResponse.objects.get(entity=entity)
                    esi_entity_contract_response.data = json.dumps(esi_contract_response, indent=4, sort_keys=True, default=str)
                    esi_entity_contract_response.save()
                    print("updated esi corporation contract response for entity_id: {}".format(entity.entity_id))
                else:
                    esi_entity_contract_response = EsiEntityContractResponse(
                        entity = entity,
                        data=json.dumps(esi_contract_response, indent=4, sort_keys=True, default=str)
                    )
                    esi_entity_contract_response.save()
                    print("created esi corporation contract response for entity_id: {}".format(entity.entity_id))

            if entity.type == 'character':
                print("updating esi character contract response for entity_id: {}".format(entity.entity_id))
                required_scopes = ['esi-contracts.read_character_contracts.v1']
                token = Token.get_token(entity.entity_id, required_scopes)
                esi_contract_response = esi.client.Contracts.get_characters_character_id_contracts(character_id=entity.entity_id, token=token.valid_access_token()).results()

                if EsiEntityContractResponse.objects.filter(entity=entity).exists():
                    esi_entity_contract_response = EsiEntityContractResponse.objects.get(entity=entity)
                    esi_entity_contract_response.data = json.dumps(esi_contract_response, indent=4, sort_keys=True, default=str)
                    esi_entity_contract_response.save()
                else:
                    esi_entity_contract_response = EsiEntityContractResponse(
                        entity = entity,
                        data=json.dumps(esi_contract_response, indent=4, sort_keys=True, default=str)
                    )
                    esi_entity_contract_response.save()
            print("updated esi corporation contract response for entity_id: {}".format(entity.entity_id))
        except Exception as e:
            print("failed to update esi corporation contract response for entity_id: {}".format(entity.entity_id))
            print(e)

@app.task()
def create_entity_tax_report():
    contract_entity_tax_responses, total_estimated_sales, total_estimated_tax = get_entity_taxes()
    tax_report_blob = ""
    for tax_response in contract_entity_tax_responses:
        tax_report_blob += str(tax_response.entity_name) + "\t" + str(tax_response.estimated_tax) + "\n"

    tax_report = EveContractTaxReport(report=tax_report_blob)
    tax_report.save()

@app.task()
def create_eve_contracts():
    for response in EsiEntityContractResponse.objects.all():
        data = json.loads(response.data)
        for contract in data:
            if contract['type'] != 'item_exchange':
                continue
            # clean up old contracts
            if EveContract.objects.filter(contract_id=contract['contract_id']).exists():
                eve_contract = EveContract.objects.get(contract_id=contract['contract_id'])
                if (contract['status'] == 'outstanding' or contract['status'] == 'finished'):
                    eve_contract.status = contract['status']
                    eve_contract.save()
                else:
                    eve_contract.delete()
                continue 
            
            # create new contracts
            if not EveFitting.objects.filter(name=contract['title']):
                continue
            if contract['status'] == 'outstanding' or contract['status'] == 'finished':
                eve_contract = EveContract.objects.create(
                    contract_id=contract['contract_id'],
                    status=contract['status'],
                    title=contract['title'],
                    price=contract['price'],
                    assignee_id=contract['assignee_id'],
                    acceptor_id=contract['acceptor_id'],
                    issuer_external_id=contract['issuer_id'],
                    fitting=EveFitting.objects.get(name=contract['title'])
                )
                issuer_id = contract['issuer_id']
                issuer_corporation_id = contract['issuer_corporation_id']
                if EveContractEntity.objects.filter(entity_id=issuer_id).exists():
                    issuer = EveContractEntity.objects.get(entity_id=issuer_id)
                    eve_contract.issuer = issuer
                    eve_contract.save()
                elif EveContractEntity.objects.filter(entity_id=issuer_corporation_id).exists():
                    issuer = EveContractEntity.objects.get(entity_id=issuer_corporation_id)
                    eve_contract.issuer = issuer
                    eve_contract.save()
                else:
                    logger.error("Could not find issuer for contract %s", contract['contract_id'])