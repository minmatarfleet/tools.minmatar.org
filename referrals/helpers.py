from .models import  EveCharacterResourceLinkClick
from eve_auth.models import UserEveCharacter
from .views import LeaderboardResponse, payout_pool

from pydantic import BaseModel

def get_leaderboard_responses():
    resource_stats = []
    clicks = EveCharacterResourceLinkClick.objects.all().exclude(character_id__in=[634915984])
    character_ids = {}
    total_clicks = 0
    for click in clicks:
        if click.character_id not in character_ids:
            character_ids[click.character_id] = 1
            total_clicks += 1
        else:
            character_ids[click.character_id] += 1
            total_clicks += 1

    # subtract from total clicks to account for removed characters
    total_clicks -= sum([v for k, v in character_ids.items() if v < 10])

    # remove all characters with less than 10 clicks
    character_ids = {k: v for k, v in character_ids.items() if v >= 10}


    for character_id, clicks in character_ids.items():
        character = UserEveCharacter.objects.get(character_id=character_id)
        resource_stats.append(LeaderboardResponse(character_id=character_id, name=character.character_name, clicks=clicks, payout=round(payout_pool*(clicks/total_clicks))))

    # sort resource_stats by click attribute
    resource_stats.sort(key=lambda x: x.clicks, reverse=True)
    return resource_stats