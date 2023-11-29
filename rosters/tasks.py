from tools.celery  import app 
from .models import EveRoster, EveRosterMember
from esi.clients import EsiClientProvider
from esi.models import Token
import requests 
from datetime import datetime, timedelta
from discoPy.rest.client import Application, User, Guild, Channel, Stage, Webhook
from django.conf import settings
from .helpers import get_eve_character_for_discord_username
from django.utils import timezone

esi = EsiClientProvider()

@app.task()
def get_fc_stats(days=14):
    token = settings.DISCORD_BOT_TOKEN
    channel = Channel(token=token)
    data = {}
    threads = []
    threads_response = channel.list_public_archived_threads(channel_id=1069380111897481256, limit=100)
    for thread in threads_response['threads']:
        threads.append(thread)

    guild = Guild(token=token)
    threads_response = guild = guild.list_active_threads(guild_id=1041384161505722368)
    for thread in threads_response['threads']:
        if int(thread['parent_id']) != 1069380111897481256:
            print("skipping thread, not in aars channel: {}".format(thread['name']))
            continue
        threads.append(thread)

    for thread in threads:
        # load threads_response['threads'][0]['thread_metadata']['create_timestamp'] into datetime
        # format: 2023-03-15T20:23:41.483247+00:00
        thread_created_time = datetime.strptime(thread['thread_metadata']['create_timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')
        # skip threads older than 30 days
        if thread_created_time < timezone.now() - timedelta(days=days):
            print("skipping thread, older than 30 days: {}".format(thread['name']))
            continue

        if thread['owner_id'] not in data:
            data[thread['owner_id']] = 0

        data[thread['owner_id']] += 1
        print("logging thread: {}".format(thread['name']))

    response = {}
    for key, value in data.items():
        try:
            character_name = get_eve_character_for_discord_username(key)
        except Exception as e:
            print("failed to get character name for discord id: {}".format(key))
            continue
        response[character_name] = value
    
    return response

def get_fc_report():
    two_week_stats = get_fc_stats(14)
    month_stats = get_fc_stats(30)
    three_month_stats = get_fc_stats(90)

    with open('exports/fc_report.txt', 'w') as f:
        f.write("FC\t2w\t1m\t3m\n")
        for key, value in three_month_stats.items():
            f.write(f"{key}\t{two_week_stats.get(key, None)}\t{month_stats.get(key, None)}\t{three_month_stats.get(key, None)}\n")

@app.task()
def update_rosters():
    EveRosterMember.objects.all().delete()
    counter = 0
    for roster in EveRoster.objects.all():
        if not roster.active:
            print("skipping roster {}, is not active".format(roster.corporation_id))
            continue

        required_scopes = ['esi-corporations.read_corporation_membership.v1']
        token = Token.get_token(roster.ceo_id, required_scopes)
        if not token:
            print("skipping roster {}, no token".format(roster.corporation_id))
            continue
        # get corporation members 
        esi_corporation_members = esi.client.Corporation.get_corporations_corporation_id_members(corporation_id=roster.corporation_id, token=token.valid_access_token()).results()
        # trigger update_roster_member for every member 
        for member in esi_corporation_members:
            print("updating roster member %s with countdown %s" % (member, counter*2))
            update_roster_member.apply_async(args=[member, roster.pk], countdown=counter*2)
            counter += 1

@app.task()
def update_roster(corporation_name):
        counter = 0
        roster = EveRoster.objects.filter(name=corporation_name).first()
        if not roster:
            return 

        required_scopes = ['esi-corporations.read_corporation_membership.v1']
        token = Token.get_token(roster.ceo_id, required_scopes)
        if not token:
            return
        # get corporation members 
        esi_corporation_members = esi.client.Corporation.get_corporations_corporation_id_members(corporation_id=roster.corporation_id, token=token.valid_access_token()).results()
        # trigger update_roster_member for every member 
        for member in esi_corporation_members:
            print("updating roster member %s with countdown %s" % (member, counter*2))
            update_roster_member.apply_async(args=[member, roster.pk], countdown=counter*2)
            counter += 1

@app.task()
def update_roster_member(character_id, roster_pk):
    # check if member exists
    roster = EveRoster.objects.get(pk=roster_pk)
    member = EveRosterMember.objects.filter(character_id=character_id, roster=roster).first()
    if member is None:
        member = EveRosterMember(character_id=character_id, roster=roster)
    
    # get zkillboard stats
    url = f"https://zkillboard.com/api/stats/characterID/{character_id}/"
    response = requests.get(url, headers={'User-Agent': 'tools.minmatar.org'})
    if response.status_code == 200:
        data = response.json()
        member.name = data['info']['name']
        member.monthly_kills = 0
        keys = [] 
        current_time = datetime.now()
        keys.append(f"{current_time.year}{'%02d' % current_time.month}")
        current_time = current_time - timedelta(days=30)
        keys.append(f"{current_time.year}{'%02d' % current_time.month}")

        for key in keys:
            print("checking for key in zkillboard data: {}".format(key))
            if key in data['months']:
                print("found key in zkillboard data: {}".format(key))
                if 'shipsDestroyed' in data['months'][key]:
                    member.monthly_kills += data['months'][key]['shipsDestroyed']
        member.save()
    else:
        print("failed to get zkillboard data for character {}".format(character_id))
        print("response: {}".format(response))

    