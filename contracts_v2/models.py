from django.db import models
from fleets.models import EveFitting
from datetime import timedelta
from django.utils import timezone
from esi.models import Token

# Create your models here.
class EveContractLocation(models.Model):
    location_id = models.IntegerField(unique=True)
    location_name = models.CharField(max_length=255)
    friendly_location_name = models.CharField(max_length=255)
    primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.primary: 
            try:
                temp = EveContractLocation.objects.get(primary=True)
                if self != temp:
                    temp.primary = False
                    temp.save()
            except EveContractLocation.DoesNotExist:
                pass
        super(EveContractLocation, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.friendly_location_name}"
    
class EveContractExpectation(models.Model):
    fitting = models.ForeignKey(EveFitting, on_delete=models.CASCADE)
    location = models.ForeignKey(EveContractLocation, on_delete=models.CASCADE, related_name='expectations', null=True, blank=True)
    quantity = models.IntegerField()
    entities = models.ManyToManyField('EveContractEntity', blank=True, related_name='expectations')
    legacy_alias = models.CharField(max_length=255, null=True, blank=True)
    # comma separated list of contract aliases
    aliases = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('fitting', 'location')

    def __str__(self):
        return f"{self.title} - {self.location}"

    @property
    def title(self):
        return f"{self.fitting.name}"
    

class EveDoctrineExpectation(models.Model):
    doctrine = models.ForeignKey('fleets.EveDoctrine', on_delete=models.CASCADE)
    location = models.ForeignKey(EveContractLocation, on_delete=models.CASCADE, related_name='doctrine_expectations', null=True, blank=True)
    type = models.CharField(max_length=32, choices=(('public', 'Public'), ('alliance', 'Alliance')))
    entities = models.ManyToManyField('EveContractEntity', blank=True, related_name='doctrine_expectations')

    def __str__(self):
        return f"{self.doctrine.name} - {self.location}"

    @property
    def entity_str(self):
        return ", ".join([e.entity_name for e in self.entities.all()])
    
class EveContractEntity(models.Model):
    entity_id = models.IntegerField(unique=True)
    entity_name = models.CharField(max_length=255)
    type = models.CharField(max_length=32, choices=(('character', 'Character'), ('corporation', 'Corporation')))
    domain = models.CharField(max_length=32, choices=(('Public Seeding', 'Public Seeding'), ('Public Doctrine Seeding', 'Public Doctrine Seeding'), ('Alliance Doctrine Seeding', 'Alliance Doctrine Seeding')), default='Public Seeding')

    # contact information
    contact_character_name = models.CharField(max_length=255)
    contact_character_id = models.BigIntegerField() 
    contact_discord_name = models.CharField(max_length=255)
    contact_discord_id = models.BigIntegerField()

    # extra fields for corporation type ids
    ceo_id = models.IntegerField(null=True, blank=True)

    @property
    def has_token(self):
        if self.type == 'corporation':
            required_scopes = ['esi-contracts.read_corporation_contracts.v1']
            token = Token.get_token(self.ceo_id, required_scopes)
        if self.type == 'character':
            required_scopes = ['esi-contracts.read_character_contracts.v1']
            token = Token.get_token(self.entity_id, required_scopes)

        if token:
            return True
        return False
    def __str__(self):
        return f"{self.entity_name}"

class EveContractEntityCodeChallenge(models.Model):
    entity_id = models.IntegerField()
    entity_name = models.CharField(max_length=255)
    type = models.CharField(max_length=32, choices=(('character', 'Character'), ('corporation', 'Corporation')))
    challenge = models.CharField(max_length=36)

class EveContractEntityManager(models.Model):
    entity = models.ForeignKey(EveContractEntity, on_delete=models.CASCADE)
    character_id = models.IntegerField()

    def __str__(self):
        return f"{self.entity.entity_name} - {self.character_id}"

def get_start_range():
    return timezone.now() - timedelta(days=30)
def get_end_range():
    return timezone.now()

class EveContractTaxReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    start_range = models.DateField(default=get_start_range)
    end_range = models.DateField(default=get_end_range)
    # text blob of \t separated entity names with their tax for the month
    report = models.TextField()

    def __str__(self):
        return f"{self.start_range} - {self.end_range}"

class EveContract(models.Model):
    from fleets.models import EveFitting
    contract_id = models.BigIntegerField(unique=True)
    status = models.CharField(max_length=32, choices=(('outstanding', 'Outstanding'), ('completed', 'Completed')))
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=32, decimal_places=2)
    assignee_id = models.IntegerField(null=True, blank=True)
    acceptor_id = models.IntegerField(null=True, blank=True)
    issuer_external_id = models.IntegerField()

    # audit fields
    created_at = models.DateTimeField(auto_now_add=True)

    # relationships
    issuer = models.ForeignKey(EveContractEntity, on_delete=models.SET_NULL, null=True, blank=True)
    fitting = models.ForeignKey(EveFitting, on_delete=models.SET_NULL, null=True, blank=True)

class EsiEntityContractResponse(models.Model):
    entity = models.ForeignKey(EveContractEntity, on_delete=models.CASCADE, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    data = models.TextField()