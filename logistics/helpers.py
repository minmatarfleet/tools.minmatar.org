from .models import EsiCourierEntityResponse
import json 
from pydantic import BaseModel 

class CourierHistoricalStatistics(BaseModel):
    total_contracts: int
    total_volume: float
    total_reward: float
    total_collateral: float
    character_metrics: dict

class CourierCurrentStatistics(BaseModel):
    total_contracts: int
    total_volume: float
    total_reward: float
    total_collateral: float

def get_volume_information():
    esi_entity_contract_responses = EsiCourierEntityResponse.objects.all()
    response = {}
    for esi_entity_contract_response in esi_entity_contract_responses:
        esi_contract_response = json.loads(esi_entity_contract_response.data)
        for contract in esi_contract_response:
            if contract['type'] == 'courier' and contract['status'] == 'finished':
                if contract['issuer_id'] not in response:
                    response[contract['issuer_id']] = []

                response[contract['issuer_id']].append(contract['volume'])

    return response

def get_historical_statistics():
    esi_entity_contract_responses = EsiCourierEntityResponse.objects.all()
    total_volume = 0.0
    total_collateral = 0.0
    total_reward = 0.0
    total_contracts = 0
    character_metrics = {}
    for esi_entity_contract_response in esi_entity_contract_responses:
        esi_contract_response = json.loads(esi_entity_contract_response.data)
        for contract in esi_contract_response:
            if contract['type'] == 'courier' and contract['status'] == 'finished':
                if contract['acceptor_id'] not in character_metrics:
                    character_metrics[contract['acceptor_id']] = 1
                else:
                    character_metrics[contract['acceptor_id']] += 1
                total_contracts += 1
                total_volume += contract['volume']
                total_reward += contract['reward']
                total_collateral += contract['collateral']

    return CourierHistoricalStatistics(
        total_contracts=total_contracts,
        total_volume=total_volume,
        total_reward=total_reward,
        total_collateral=total_collateral,
        character_metrics=character_metrics
    )


def get_current_statistics():
    esi_entity_contract_responses = EsiCourierEntityResponse.objects.all()
    total_contracts = 0
    total_volume = 0.0
    total_collateral = 0.0
    total_reward = 0.0
    for esi_entity_contract_response in esi_entity_contract_responses:
        esi_contract_response = json.loads(esi_entity_contract_response.data)
        for contract in esi_contract_response:
            if contract['type'] == 'courier' and contract['status'] == 'outstanding':
                total_contracts += 1
                total_volume += contract['volume']
                total_reward += contract['reward']
                total_collateral += contract['collateral']

    return CourierCurrentStatistics(
        total_contracts=total_contracts,
        total_volume=total_volume,
        total_reward=total_reward,
        total_collateral=total_collateral
    )