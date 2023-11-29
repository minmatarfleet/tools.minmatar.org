from tools.celery  import app 
from .models import EveCourierEntity, EveCourierPilot, EsiCourierEntityResponse
from esi.clients import EsiClientProvider
from esi.models import Token
import logging 
from discoPy.rest.client import Application, User, Guild, Channel, Stage, Webhook
from django.conf import settings
import json
from datetime import datetime 
from dateutil import parser

logger = logging.getLogger(__name__)

esi = EsiClientProvider()

@app.task()
def update_esi_courier_entity_responses():
    for entity in EveCourierEntity.objects.all():
        token = entity.token
        if not token:
            print("Skipping courier entity_id: {}".format(entity.ceo_id))
            continue

        # get contracts from esi 
        esi_contract_response = esi.client.Contracts.get_corporations_corporation_id_contracts(corporation_id=entity.corporation_id, token=token.valid_access_token()).results()
        # save response
        if EsiCourierEntityResponse.objects.filter(entity=entity).exists():
            esi_entity_contract_response = EsiCourierEntityResponse.objects.get(entity=entity)
            esi_entity_contract_response.data = json.dumps(esi_contract_response, indent=4, sort_keys=True, default=str)
            esi_entity_contract_response.save()
        else:
            esi_entity_contract_response = EsiCourierEntityResponse(
                entity = entity,
                data=json.dumps(esi_contract_response, indent=4, sort_keys=True, default=str)
            )
            esi_entity_contract_response.save()


@app.task()
def notify_discord_courier_contracts():
    token = settings.DISCORD_BOT_TOKEN
    channel = Channel(token=token)
    message = "**Courier notice" + "**\n"
    message += "*This message occurs every 12 hours if there are valid contracts.*\n\n"
    for esi_courier_entity_response in EsiCourierEntityResponse.objects.all():
        contracts_data = json.loads(esi_courier_entity_response.data)
        contracts = []
        total_m3 = 0.0
        total_reward = 0.0
        total_collateral = 0.0
        for contract in contracts_data:
            if contract['type'] == 'courier' and contract['status'] == 'outstanding' and contract['assignee_id'] == esi_courier_entity_response.entity.corporation_id:
                start_id = int(contract['start_location_id'])
                end_id = int(contract['end_location_id'])

                if start_id > 60000000 and start_id < 61000000:
                    system_id = esi.client.Universe.get_universe_stations_station_id(station_id=start_id).results()['system_id']
                    system_name = esi.client.Universe.get_universe_systems_system_id(system_id=system_id).results()['name']
                    start_location = system_name
                else: 
                    start_location = "Structure"

                if end_id > 60000000 and end_id < 61000000:
                    system_id = esi.client.Universe.get_universe_stations_station_id(station_id=end_id).results()['system_id']
                    system_name = esi.client.Universe.get_universe_systems_system_id(system_id=system_id).results()['name']
                    end_location = system_name
                else:
                    end_location = "Structure"

                total_m3 += contract['volume']
                total_reward += contract['reward']
                total_collateral += contract['collateral']

                # subtract date_issued from today
                date_issued = parser.parse(contract['date_issued'])
                time_delta = datetime.now().replace(tzinfo=None) - date_issued.replace(tzinfo=None)
                age = f"{time_delta.days}d{time_delta.seconds//3600}h{time_delta.seconds//60%60}m"

                size = contract['volume']
                size = f'{size:,} m3' 
                message += f"- {start_location} to {end_location} | {size} | {age} \n"
                contracts.append(contract)

    if len(contracts) == 0:
        return # no notifications to send

    # add total values to message
    message += "\n"
    message += f"Total m3: {total_m3:,}\n"
    message += f"Total reward: {total_reward:,}\n"
    message += f"Total collateral: {total_collateral:,}\n"
    message += "\n"
    message += "*Want to help haul contracts with your DST/BR/JF character? Request the Standard Freight role at https://auth.minmatar.org/groups/ and mail BearThatCares for next steps.*"

    if message != "":
        channel.create_message(channel_id='1062178037875081226', content=message)