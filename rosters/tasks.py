from tools.celery import app
from .models import EveRoster, EveRosterMember
from esi.clients import EsiClientProvider
from esi.models import Token
import requests
from datetime import datetime, timedelta
from discoPy.rest.client import Application, User, Guild, Channel, Stage, Webhook
from django.conf import settings
from django.utils import timezone
from fleets.models import EsiFleet, EsiFleetMember

esi = EsiClientProvider()


def get_fc_report():
    two_week_stats = get_fc_stats(14)
    month_stats = get_fc_stats(30)
    three_month_stats = get_fc_stats(90)

    with open("exports/fc_report.txt", "w") as f:
        f.write("FC\t2w\t1m\t3m\n")
        for key, value in three_month_stats.items():
            f.write(
                f"{key}\t{two_week_stats.get(key, None)}\t{month_stats.get(key, None)}\t{three_month_stats.get(key, None)}\n"
            )


@app.task()
def update_rosters():
    EveRosterMember.objects.all().delete()
    counter = 0
    for roster in EveRoster.objects.all():
        if not roster.active:
            print("skipping roster {}, is not active".format(roster.corporation_id))
            continue

        required_scopes = ["esi-corporations.read_corporation_membership.v1"]
        token = Token.get_token(roster.ceo_id, required_scopes)
        if not token:
            print("skipping roster {}, no token".format(roster.corporation_id))
            continue
        # get corporation members
        esi_corporation_members = (
            esi.client.Corporation.get_corporations_corporation_id_members(
                corporation_id=roster.corporation_id, token=token.valid_access_token()
            ).results()
        )
        # trigger update_roster_member for every member
        for member in esi_corporation_members:
            print("updating roster member %s with countdown %s" % (member, counter * 2))
            update_roster_member.apply_async(
                args=[member, roster.pk], countdown=counter * 2
            )
            counter += 1


@app.task()
def update_roster(corporation_name):
    counter = 0
    roster = EveRoster.objects.filter(name=corporation_name).first()
    if not roster:
        return

    required_scopes = ["esi-corporations.read_corporation_membership.v1"]
    token = Token.get_token(roster.ceo_id, required_scopes)
    if not token:
        return
    # get corporation members
    esi_corporation_members = (
        esi.client.Corporation.get_corporations_corporation_id_members(
            corporation_id=roster.corporation_id, token=token.valid_access_token()
        ).results()
    )
    # trigger update_roster_member for every member
    for member in esi_corporation_members:
        print("updating roster member %s with countdown %s" % (member, counter * 2))
        update_roster_member.apply_async(
            args=[member, roster.pk], countdown=counter * 2
        )
        counter += 1


@app.task()
def update_roster_member(character_id, roster_pk):
    # check if member exists
    roster = EveRoster.objects.get(pk=roster_pk)
    member = EveRosterMember.objects.filter(
        character_id=character_id, roster=roster
    ).first()
    if member is None:
        member = EveRosterMember(character_id=character_id, roster=roster)

    # get zkillboard stats
    url = f"https://zkillboard.com/api/stats/characterID/{character_id}/"
    response = requests.get(url, headers={"User-Agent": "tools.minmatar.org"})
    if response.status_code == 200:
        data = response.json()
        member.name = data["info"]["name"]
        member.monthly_kills = 0
        member.quarterly_kills = 0

        # calculate monthly kills
        keys = []
        current_time = datetime.now()
        keys.append(f"{current_time.year}{'%02d' % current_time.month}")
        current_time = current_time - timedelta(days=30)
        keys.append(f"{current_time.year}{'%02d' % current_time.month}")

        for key in keys:
            print("checking for key in zkillboard data: {}".format(key))
            if key in data["months"]:
                print("found key in zkillboard data: {}".format(key))
                if "shipsDestroyed" in data["months"][key]:
                    member.monthly_kills += data["months"][key]["shipsDestroyed"]

        # calculate quarterly kills
        keys = []
        keys.append(f"{current_time.year}{'%02d' % current_time.month}")
        current_time = current_time - timedelta(days=30)
        keys.append(f"{current_time.year}{'%02d' % current_time.month}")
        current_time = current_time - timedelta(days=60)
        keys.append(f"{current_time.year}{'%02d' % current_time.month}")
        current_time = current_time - timedelta(days=90)

        for key in keys:
            print("checking for key in zkillboard data: {}".format(key))
            if key in data["months"]:
                print("found key in zkillboard data: {}".format(key))
                if "shipsDestroyed" in data["months"][key]:
                    member.quarterly_kills += data["months"][key]["shipsDestroyed"]

        monthly_esi_fleet_count = EsiFleetMember.objects.filter(
            character_id=character_id,
            fleet__start_time__gte=timezone.now() - timezone.timedelta(days=30),
        ).count()
        quarterly_esi_fleet_count = EsiFleetMember.objects.filter(
            character_id=character_id,
            fleet__start_time__gte=timezone.now() - timezone.timedelta(days=90),
        ).count()
        member.monthly_fleets = monthly_esi_fleet_count
        member.quarterly_fleets = quarterly_esi_fleet_count
        member.save()
    else:
        print("failed to get zkillboard data for character {}".format(character_id))
        print("response: {}".format(response))


@app.task()
def populate_main_characters():
    from fleets.authorization import get_main_character_id

    character_ids = set()
    for member in EveRosterMember.objects.all():
        if member.main_character_id is None:
            member.main_character_id = get_main_character_id(member.character_id)
            character_ids.add(member.main_character_id)
            member.save()

    # resolve names
    esi_characters = esi.client.Universe.post_universe_names(
        ids=list(character_ids)
    ).results()
    for character in esi_characters:
        member = EveRosterMember.objects.filter(
            main_character_id=character["id"]
        ).first()
        if member:
            member.main_character_name = character["name"]
            member.save()
