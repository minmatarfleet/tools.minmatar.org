from eveuniverse.models import EveEntity, EveType, EveGroup

from fleets import eft
from tools.celery import app
from git import Repo
import os
import shutil
from .helpers import type_id_to_group_name
from .models import EveFitting, EsiFleet, EsiFleetMember, EsiFleetMemberTrackingLog
from esi.clients import EsiClientProvider
from discoPy.rest.client import Application, User, Guild, Channel, Stage, Webhook
from django.conf import settings
from esi.models import Token
from bravado.exception import HTTPNotFound
from django.utils import timezone
import logging
from django.db.models import Q


logger = logging.getLogger(__name__)

esi = EsiClientProvider()

valid_file_prefixes = [
    '[FL33T]',
    '[NVY-1]',
    '[NVY-5]',
    '[NVY-30]',
    '[ADV-5]',
    '[ADV-30]',
    '[POCHVEN]',
]

@app.task()
def update_fittings():
    PATH = './exports/fittings'
    shutil.rmtree(PATH, ignore_errors=True)
    repo = Repo.clone_from("https://github.com/Minmatar-Fleet-Alliance/FL33T-Fits", PATH)
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if os.path.splitext(f)[1] == '.md']

    current_version = repo.head.object.hexsha
    
    # resolve names to save ESI calls
    names = set() 
    for file in files:
        # skip files that contain no valid prefixes 
        if not any(prefix in file for prefix in valid_file_prefixes):
            continue

        if "Archived" in file:
            continue

        # open and read file 
        with open(file, 'r') as f:
            data = f.readlines()
            line = data.pop(0)
            if line.startswith('#'):
                names.add(line.replace('#', '').strip())
    
    # fetch ship type ids and names from universe
    # need to pass update=True here, otherwise ESI is not checked if any of the ships already exist in local db
    ship_type_ids = {e.name: e.id for e in EveEntity.objects.fetch_by_names_esi(names=names, update=True).filter(category=EveEntity.CATEGORY_INVENTORY_TYPE)}
    ship_type_names = {name: type_id_to_group_name(id) for name, id in ship_type_ids.items()}

    # parse files for fittings 
    names = set()
    for file in files:
        # skip files that contain no valid prefixes 
        if not any(prefix in file for prefix in valid_file_prefixes):
            continue

        if "Archived" in file:
            continue
        # get file name and strip md extension
        fitting_name = os.path.basename(file).replace('.md', '')

        # open and read file 
        name = None 
        description = None
        fitting = None 
        
        with open(file, 'r') as f:
            data = f.readlines()

            try: 
                while name is None:
                    line = data.pop(0)
                    if line.startswith('#'):
                        name = line.replace('#', '').strip()
                    while not line.startswith('## Description'):
                        line = data.pop(0)

                while description is None:
                    if line.startswith('## Description'):
                        description = ""
                        line = data.pop(0)
                        while not line.startswith('## Fit'):
                            description += line
                            line = data.pop(0)

                while fitting is None:
                    if line.startswith('## Fit'):
                        while line.startswith("```") or line.startswith("##") or line.startswith("\n"):
                            line = data.pop(0)
                        fitting = ""
                        while not line.startswith('```'):
                            fitting += line
                            line = data.pop(0)
            except Exception as e:
                pass

        if name and description and fitting:
            names.add(fitting_name)
            if EveFitting.objects.filter(name=fitting_name).exists():
                current_fitting = EveFitting.objects.get(name=fitting_name)
                if current_version != current_fitting.latest_version:
                    print("fitting out of date. updating fitting: %s" % fitting_name)
                    current_fitting.latest_version = current_version
                    current_fitting.description = description
                    current_fitting.eft_format = fitting
                    current_fitting.multibuy_format = ""
                    current_fitting.build_updated = False
                    current_fitting.fl33t_updated = False
                    current_fitting.notified = False
                    current_fitting.save()
                    # parse the fit to get eveuniverse to cache the items
                    eft.parse_eft(current_fitting.eft_format)
                else:
                    print("fitting up to date. skipping fitting: %s" % fitting_name)
            else:
                print("creating fitting: %s" % fitting_name)
                fitting = EveFitting.objects.create(
                    name=fitting_name,
                    description=description,
                    ship_name=name,
                    ship_type_id=ship_type_ids[name],
                    ship_type_name=ship_type_names[name],
                    eft_format=fitting,
                    multibuy_format="",
                    latest_version=current_version
                )
                # parse the fit to get eveuniverse to cache the items
                eft.parse_eft(fitting.eft_format)
        else:
            print("failed to parse file: %s" % file)

    names = list(names)
    EveFitting.objects.filter(~Q(name__in=names)).delete()
@app.task()
def notify_discord_fitting_updates():
    host = "https://tools.minmatar.org"
    token = settings.DISCORD_BOT_TOKEN
    channel = Channel(token=token)

    fittings = EveFitting.objects.filter(notified=False)
    send = False

    message = "*One or more fittings are out of date. Please update them when convenient.*\n"
    message += "**[BUILD] fittings that are out of date**\n"
    for fitting in fittings:
        if fitting.build_updated:
            continue
        send = True
        message += "- " + fitting.name + "\n"
    message += "To mark all of these complete, click: %s/fleets/fittings/mark_as_complete/build/\n" % host 

    message += "\n**[FL33T] fittings that are out of date**\n"
    for fitting in fittings:
        if fitting.fl33t_updated:
            continue
        send = True
        message += "- " + fitting.name + "\n"
    message += "To mark all of these complete, click: %s/fleets/fittings/mark_as_complete/fl33t/\n" % host 

    if send:
        channel.create_message(channel_id='1083910089511010335', content=message)

@app.task()
def update_esi_fleets():
    fleets = EsiFleet.objects.filter(end_time=None)
    logger.info("Updating %s fleets" % fleets.count())
    for fleet in fleets:
        required_scopes = ['esi-fleets.read_fleet.v1']
        token = Token.get_token(fleet.fleet.fleet_commander_id, required_scopes)
        try:
            esi_fleet = esi.client.Fleets.get_fleets_fleet_id(fleet_id=fleet.id, token=token.valid_access_token()).results()
            fleet.is_free_move = esi_fleet['is_free_move']
            fleet.is_registered = esi_fleet['is_registered']
            fleet.is_voice_enabled = esi_fleet['is_voice_enabled']
            fleet.motd = esi_fleet['motd']
            fleet.save()
            update_esi_fleet_members(fleet.id)
        except HTTPNotFound as e:
            fleet.end_time = timezone.now()
            fleet.save()

@app.task()
def update_esi_fleet_members(esi_fleet_id):
    esi_fleet = EsiFleet.objects.get(id=esi_fleet_id)
    required_scopes = ['esi-fleets.read_fleet.v1']
    token = Token.get_token(esi_fleet.fleet.fleet_commander_id, required_scopes)
    esi_fleet_members = esi.client.Fleets.get_fleets_fleet_id_members(fleet_id=esi_fleet_id, token=token.valid_access_token()).results()
    
    ids_to_resolve = set()
    for esi_fleet_member in esi_fleet_members:
        ids_to_resolve.add(esi_fleet_member['character_id'])
        ids_to_resolve.add(esi_fleet_member['ship_type_id'])
        ids_to_resolve.add(esi_fleet_member['solar_system_id'])

    ids_to_resolve = list(ids_to_resolve)
    resolved_ids = esi.client.Universe.post_universe_names(ids=ids_to_resolve).results()
    resolved_ids = {x['id']: x['name'] for x in resolved_ids}

    for esi_fleet_member in esi_fleet_members:
        if EsiFleetMember.objects.filter(character_id=esi_fleet_member['character_id'], fleet=esi_fleet).exists():
            existing_esi_fleet_member = EsiFleetMember.objects.get(character_id=esi_fleet_member['character_id'], fleet=esi_fleet)

            if existing_esi_fleet_member.ship_type_id != esi_fleet_member['ship_type_id'] or existing_esi_fleet_member.solar_system_id != esi_fleet_member['solar_system_id']:
                EsiFleetMemberTrackingLog.objects.create(
                    esi_fleet_member=existing_esi_fleet_member,
                    ship_type_id=existing_esi_fleet_member.ship_type_id,
                    solar_system_id=existing_esi_fleet_member.solar_system_id,
                    ship_name=existing_esi_fleet_member.ship_name,
                    solar_system_name=existing_esi_fleet_member.solar_system_name,
                ) 
            
            existing_esi_fleet_member.join_time=esi_fleet_member['join_time']
            existing_esi_fleet_member.role=esi_fleet_member['role']
            existing_esi_fleet_member.role_name=esi_fleet_member['role_name']
            existing_esi_fleet_member.ship_type_id=esi_fleet_member['ship_type_id']
            existing_esi_fleet_member.solar_system_id=esi_fleet_member['solar_system_id']
            existing_esi_fleet_member.squad_id=esi_fleet_member['squad_id']
            existing_esi_fleet_member.station_id=esi_fleet_member['station_id']
            existing_esi_fleet_member.takes_fleet_warp=esi_fleet_member['takes_fleet_warp']
            existing_esi_fleet_member.wing_id=esi_fleet_member['wing_id']
            existing_esi_fleet_member.character_name=resolved_ids[esi_fleet_member['character_id']]
            existing_esi_fleet_member.ship_name=resolved_ids[esi_fleet_member['ship_type_id']]
            existing_esi_fleet_member.solar_system_name=resolved_ids[esi_fleet_member['solar_system_id']]
            existing_esi_fleet_member.save()
        else:
            try:
                created_esi_fleet_member = EsiFleetMember.objects.create(
                    fleet=esi_fleet,
                    character_id=esi_fleet_member['character_id'],
                    join_time=esi_fleet_member['join_time'],
                    role=esi_fleet_member['role'],
                    role_name=esi_fleet_member['role_name'],
                    ship_type_id=esi_fleet_member['ship_type_id'],
                    solar_system_id=esi_fleet_member['solar_system_id'],
                    squad_id=esi_fleet_member['squad_id'],
                    station_id=esi_fleet_member['station_id'],
                    takes_fleet_warp=esi_fleet_member['takes_fleet_warp'],
                    wing_id=esi_fleet_member['wing_id'],
                    character_name=resolved_ids[esi_fleet_member['character_id']],
                    ship_name=resolved_ids[esi_fleet_member['ship_type_id']],
                    solar_system_name=resolved_ids[esi_fleet_member['solar_system_id']],
                )

                EsiFleetMemberTrackingLog.objects.create(
                    esi_fleet_member=created_esi_fleet_member,
                    ship_type_id=created_esi_fleet_member.ship_type_id,
                    solar_system_id=created_esi_fleet_member.solar_system_id,
                    ship_name=created_esi_fleet_member.ship_name,
                    solar_system_name=created_esi_fleet_member.solar_system_name,
                )
            except Exception as e:
                logger.error(e)
