from .models import EveFleet
from django.db.models import Q
from django.utils import timezone

def get_list_of_fleets_notification():
    query = Q(start_time__gte=timezone.now() - timezone.timedelta(minutes=15))
    fleets = EveFleet.objects.filter(query).order_by('start_time')
    fleet_list_row = ""
    for fleet in fleets:
        if fleet.active:
            continue 

        unix_timestamp = int(fleet.start_time.timestamp())
        
        fleet_row = "" 
        fleet_row += f"[{fleet.type.upper()}](https://tools.minmatar.org/fleets/{fleet.id}/)"
        fleet_row += " | "
        fleet_row += f"{fleet.start_time.strftime('%Y-%m-%d %H:%M')} EVE"
        fleet_row += " | "
        fleet_row += f"<t:{unix_timestamp}>"
        fleet_list_row += f"- {fleet_row} \n"

    message = ""
    if fleet_list_row == "":
        message = "No upcoming fleets. Go touch grass.\n"
    else:
        message = "**List of upcoming fleets**\n"
    message += fleet_list_row
    message += "\n"

    webhook_payload = {
        "content": message,
        "components": [
            {
            "type": 1,
            "components": [
                {
                "style": 5,
                "label": "View Fleet Board",
                "url": f"https://tools.minmatar.org/fleets/",
                "disabled": False,
                "type": 2
                },
                {
                "style": 5,
                "label": "New Player Instructions",
                "url": "https://minmatar.org/guides/new-player-fleet-guide/",
                "disabled": False,
                "type": 2
                }
            ]
            }
        ],
    }
    return webhook_payload


def get_created_notification(fleet):
    time = fleet.start_time.strftime("%Y-%m-%d %H:%M")
    unix_timestamp = int(fleet.start_time.timestamp())
    webhook_payload = {
        "content": "",
        "components": [
            {
            "type": 1,
            "components": [
                {
                "style": 5,
                "label": "View Fleet Information",
                "url": f"https://tools.minmatar.org/fleets/{fleet.id}/",
                "disabled": False,
                "type": 2
                },
                {
                "style": 5,
                "label": "New Player Instructions",
                "url": "https://minmatar.org/guides/new-player-fleet-guide/",
                "disabled": False,
                "type": 2
                }
            ]
            }
        ],
        "embeds": [
            {
            "type": "rich",
            "title": "INCOMING PING TRANSMISSION...",
            "description": f"NOTICE OF AN **UPCOMING** {fleet.type.upper()} FLEET OPERATION.\n\nSTAGING SYSTEM: {fleet.staging.friendly_location_name}\nUNIVERSE TIME: {time}\nLOCAL TIME: <t:{unix_timestamp}>\n",
            "color": 0x18ed09,
            "author": {
                "name": f"{fleet.fleet_commander_name}",
                "icon_url": f"https://images.evetech.net/characters/{fleet.fleet_commander_id}/portrait?size=32"
            },
            "url": "https://tools.minmatar.org/fleets/",
            "footer": {
                "text": "Minmatar Fleet Alliance",
                "icon_url": "https://minmatar.org/wp-content/uploads/2023/04/Logo13.png",
            }
            }
        ]
    }
    return webhook_payload

def get_preping_notification(fleet):
    time = fleet.start_time.strftime("%Y-%m-%d %H:%M")
    unix_timestamp = int(fleet.start_time.timestamp())
    webhook_payload = {
        "content": "",
        "components": [
            {
            "type": 1,
            "components": [
                {
                "style": 5,
                "label": "View Fleet Information",
                "url": f"https://tools.minmatar.org/fleets/{fleet.id}/",
                "disabled": False,
                "type": 2
                },
                {
                "style": 5,
                "label": "New Player Instructions",
                "url": "https://minmatar.org/guides/new-player-fleet-guide/",
                "disabled": False,
                "type": 2
                }
            ]
            }
        ],
        "embeds": [
            {
            "type": "rich",
            "title": "INCOMING PRE-PING TRANSMISSION...",
            "description": f"MAXIMUM PILOTS REQUESTED FOR AN **UPCOMING** {fleet.type.upper()} FLEET OPERATION.\n\nSTAGING SYSTEM: {fleet.staging.friendly_location_name}\nUNIVERSE TIME: {time}\nLOCAL TIME: <t:{unix_timestamp}>\n",
            "color": 0xe3d618,
            "author": {
                "name": f"{fleet.fleet_commander_name}",
                "icon_url": f"https://images.evetech.net/characters/{fleet.fleet_commander_id}/portrait?size=32"
            },
            "url": "https://tools.minmatar.org/fleets/",
            "footer": {
                "text": "Minmatar Fleet Alliance",
                "icon_url": "https://minmatar.org/wp-content/uploads/2023/04/Logo13.png",
            }
            }
        ]
    }
    return webhook_payload

def get_ping_notification(fleet):
    webhook_payload = {
        "content": "@everyone",
        "components": [
            {
            "type": 1,
            "components": [
                {
                "style": 5,
                "label": "View Fleet Information",
                "url": f"https://tools.minmatar.org/fleets/{fleet.id}/",
                "disabled": False,
                "type": 2
                },
                {
                "style": 5,
                "label": "New Player Instructions",
                "url": "https://minmatar.org/guides/new-player-fleet-guide/",
                "disabled": False,
                "type": 2
                }
            ]
            }
        ],
        "embeds": [
            {
            "type": "rich",
            "title": "INCOMING FORMING TRANSMISSION...",
            "description": f"FORMING **{fleet.type.upper()}** FLEET OPERATION.\n\nSTAGING SYSTEM: {fleet.staging.friendly_location_name}\nUNIVERSE TIME: NOW\n\n DETAILS: {fleet.description}\n",
            "color": 0xe10f0f,
            "author": {
                "name": f"{fleet.fleet_commander_name}",
                "icon_url": f"https://images.evetech.net/characters/{fleet.fleet_commander_id}/portrait?size=32"
            },
            "url": "https://tools.minmatar.org/fleets/",
            "footer": {
                "text": "Minmatar Fleet Alliance",
                "icon_url": "https://minmatar.org/wp-content/uploads/2023/04/Logo13.png",
            }
            }
        ]
    }
    return webhook_payload