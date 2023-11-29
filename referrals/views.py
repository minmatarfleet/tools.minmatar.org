from django.shortcuts import render
from django.shortcuts import redirect
from .models import EveCharacterResourceLink, EveCharacterResourceLinkClick
from eve_auth.models import UserEveCharacter

from pydantic import BaseModel

payout_pool = 1500000000
resources = [
    'freight_guide',
    'ship_contracts_guide',
    'lp_guide',
]

resource_links = {
    "freight_guide": "https://minmatar.org/guides/minmatar-freight-service/",
    "ship_contracts_guide": "https://minmatar.org/guides/minmatar-public-contracts/",
    "lp_guide": "https://minmatar.org/guides/new-player/converting-loyalty-points/",
}

resource_slogans = {
    "lp_guide": "Convert your LP to ISK",
    "freight_guide": 'Ship directly from Jita to the frontlines and save your ISK!',
    "ship_contracts_guide": "Purchase fully fit ships directly on the frontlines!"
}


class Resource(BaseModel):
    name: str
    pk: str
    slogan: str


class ResourceStat(BaseModel):
    name: str
    clicks: int


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def index(request):
    resource_response = []
    resource_stats = []
    if request.user.is_authenticated:
        for resource in resources:
            link = EveCharacterResourceLink.objects.get_or_create(
                character_id=request.user.eve_character.character_id, resource=resource)[0]
            resource_response.append(Resource(
                name=resource, slogan=resource_slogans[resource], pk=link.pk))

        for resource in resources:
            clicks = EveCharacterResourceLinkClick.objects.filter(
                character_id=request.user.eve_character.character_id, resource_link__resource=resource).count()
            resource_stats.append(ResourceStat(name=resource, clicks=clicks))

    return render(request, 'referrals/index.html', {'resources': resource_response, 'resource_stats': resource_stats})

class LeaderboardResponse(BaseModel):
    character_id: int
    name: str
    clicks: int
    payout: float

def leaderboard(request):
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

    return render(request, 'referrals/leaderboard.html', {'resource_stats': resource_stats})

def register_link_click(request, character_id, resource, resource_pk):
    link = EveCharacterResourceLink.objects.get(pk=resource_pk)
    if EveCharacterResourceLinkClick.objects.filter(resource_link=link, ip=get_client_ip(request)).exists():
        return redirect(str(resource_links[resource]))

    EveCharacterResourceLinkClick.objects.create(
        character_id=character_id, resource_link=link, ip=get_client_ip(request))
        
    return redirect(str(resource_links[resource]))
