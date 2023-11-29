from django.db import models
from esi.clients import EsiClientProvider
from esi.models import Token

esi = EsiClientProvider()

# Create your models here.
class EveCourierEntity(models.Model):
    corporation_id = models.IntegerField(unique=True)
    
    # auto populated
    ceo_id = models.BigIntegerField(blank=True)
    corporation_name = models.CharField(max_length=255, blank=True)

    @property
    def token(self):
        required_scopes = ['esi-contracts.read_corporation_contracts.v1']
        return Token.get_token(self.ceo_id, required_scopes)

    @property
    def active(self):
        required_scopes = ['esi-contracts.read_corporation_contracts.v1']
        token = Token.get_token(self.ceo_id, required_scopes)
        return token
    
    def save(self, *args, **kwargs):
        esi_corporation = esi.client.Corporation.get_corporations_corporation_id(corporation_id=self.corporation_id).results()
        self.corporation_name = esi_corporation['name']
        self.ceo_id = esi_corporation['ceo_id']
        super(EveCourierEntity, self).save(*args, **kwargs)

class EveCourierPilot(models.Model):
    courier_character_id = models.BigIntegerField()
    courier_character_name = models.CharField(max_length=255)
    character_id = models.BigIntegerField(blank=True, null=True)
    character_name = models.CharField(max_length=255, blank=True, null=True)
    discord_id = models.BigIntegerField(blank=True, null=True)
    discord_name = models.CharField(max_length=255, blank=True, null=True)
    
class EsiCourierEntityResponse(models.Model):
    entity = models.ForeignKey(EveCourierEntity, on_delete=models.CASCADE)
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)