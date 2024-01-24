from django.db import models
from esi.clients import EsiClientProvider
from esi.models import Token

esi = EsiClientProvider()

# Create your models here.
class EveRoster(models.Model):
    corporation_id = models.IntegerField()
    
    # autopopulated 
    name = models.CharField(max_length=255, blank=True)
    ceo_id = models.IntegerField(blank=True)
    ticker = models.CharField(max_length=255, blank=True)
    member_count = models.IntegerField(blank=True)
    alliance_id = models.IntegerField(blank=True)
    faction_id = models.IntegerField(null=True, blank=True)

    @property
    def active(self):
        required_scopes = ['esi-corporations.read_corporation_membership.v1']
        token = Token.get_token(self.ceo_id, required_scopes)
        return token

    def save(self, *args, **kwargs):
        esi_corporation = esi.client.Corporation.get_corporations_corporation_id(corporation_id=self.corporation_id).results()
        self.name = esi_corporation['name']
        self.ceo_id = esi_corporation['ceo_id']
        self.ticker = esi_corporation['ticker']
        self.member_count = esi_corporation['member_count']
        self.alliance_id = esi_corporation['alliance_id']
        self.faction_id = esi_corporation['faction_id']
        super(EveRoster, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class EveRosterMember(models.Model):
    name = models.CharField(max_length=255)
    main_character_name = models.CharField(max_length=255, null=True, blank=True)
    character_id = models.IntegerField()
    main_character_id = models.IntegerField(null=True, blank=True)
    monthly_kills = models.IntegerField()
    quarterly_kills = models.IntegerField()
    monthly_fleets = models.IntegerField()
    quarterly_fleets = models.IntegerField()

    # autopopulated
    roster = models.ForeignKey(EveRoster, on_delete=models.CASCADE, related_name='members')