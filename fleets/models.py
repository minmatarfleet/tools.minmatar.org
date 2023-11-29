from django.db import models
from django_extensions.db.fields import AutoSlugField
from colorfield.fields import ColorField
from django.utils import timezone

fleet_types = (
    ('stratop', 'Strategic'), # alliance pings
    ('flash_form', 'Flash Form'),  # alliance pings
    ('frontline', 'Frontline'), # militia pings
    ('battlefield', 'Battlefield'), # militia pings
    ('fun_fleet', 'Fun Fleet'), # all pings
    ('random', 'Random'), # all pings
    ('training', 'Training'), # all pings
)

fleet_audiences = (
    ('militia', 'Militia'),
    ('alliance', 'Alliance'),
    ('all', 'All'),
)

fleet_type_audience_lookup = {
    'fun_fleet': 'all',
    'random': 'all',
    'training': 'all',
    'stratop': 'alliance',
    'flash_form': 'alliance',
    'frontline': 'militia',
    'battlefield': 'militia',
}

# Create your models here.
class EveFleet(models.Model):
    fleet_id = models.IntegerField(null=True, blank=True)
    fleet_commander_id = models.IntegerField(null=True, blank=True)
    fleet_commander_name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, choices=fleet_types, default="frontline")
    audience = models.CharField(max_length=255, choices=fleet_audiences, default='militia')
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    staging = models.ForeignKey('contracts_v2.EveContractLocation', null=True, on_delete=models.SET_NULL)
    doctrine = models.ForeignKey('EveDoctrine', null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def tracking_active(self):
        # get esi fleet
        try:
            esi_fleet = self.esifleet
        except EsiFleet.DoesNotExist:
            return False
        
        if self.esifleet.active:
            return True
        
        return False
    
    @property
    def tracked(self):
        # get esi fleet
        try:
            esi_fleet = self.esifleet
            return True
        except EsiFleet.DoesNotExist:
            return False

    @property
    def awaiting_ping(self):
        if self.start_time < timezone.now() and self.evefleetdiscordnotification_set.filter(type='ping').count() == 0:
            return True
        return False
    
    @property 
    def active(self):
        if self.start_time < timezone.now() and self.evefleetdiscordnotification_set.filter(type='ping').exists():
            return True
        return False

    @property
    def invalid_for_preping_reason(self):
        allowed_types = ['structure', 'stratop']
        if self.type not in allowed_types:
            return "Fleet type is not valid for preping, allowed types: %s" % allowed_types
    
        # return false if start_time is under 1 hour
        if self.start_time < timezone.now() + timezone.timedelta(hours=1):
            return "Fleet is starting too soon (within one hour) to preping"
        
        # return false if start_time is greater than 24 hours
        if self.start_time > timezone.now() + timezone.timedelta(hours=24):
            return "Fleet is starting too far in the future (more than 24 hours) to preping"
        
        if self.evefleetdiscordnotification_set.filter(type='preping').count() > 0:
            return "Notification has already been sent"
        
        return None
        
    @property
    def invalid_for_ping_reason(self):
        # start time is greater than 10 minutes
        if self.start_time > timezone.now() + timezone.timedelta(minutes=10):
            return "Fleet is starting too far in the future (more than 10 minutes) to ping"
        
        # start time has already passed 
        if self.start_time < timezone.now() + timezone.timedelta(minutes=-10):
            return "Fleet is too late to ping, must be deleted"
        
        if self.evefleetdiscordnotification_set.filter(type='ping').count() > 0:
            return "Notification has already been sent"
        
        return None 

class EveFleetDiscordWebhook(models.Model):
    name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    webhook_url = models.CharField(max_length=255, unique=True, blank=True)
    audience = models.CharField(max_length=255, choices=fleet_audiences)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        from discoPy.rest.client import Webhook
        from django.conf import settings
        token = settings.DISCORD_BOT_TOKEN
        webhook = Webhook(token=token)
        response = webhook.create_webhook(self.channel_id, self.name, avatar="https://minmatar.org/wp-content/uploads/2023/04/Logo13.png")
        self.webhook_url = response['url']
        super(EveFleetDiscordWebhook, self).save(*args, **kwargs)

class EveFleetDiscordNotification(models.Model):
    fleet_discord_notitification_types = (
        ('created', 'Created'),
        ('preping', 'Preping'),
        ('ping', 'Ping'),
    )
    type = models.CharField(max_length=255, choices=fleet_discord_notitification_types)
    fleet = models.ForeignKey('EveFleet', on_delete=models.CASCADE)

    # type and fleet are unique together
    class Meta:
        unique_together = ('type', 'fleet')

class EveFleetMOTDTemplate(models.Model):
    type = models.CharField(max_length=255, choices=fleet_types)
    audience = models.CharField(max_length=255, choices=fleet_audiences)
    motd = models.TextField()

    
class EveDoctrineTag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(populate_from="name")
    description = models.TextField()
    text_color = ColorField(default='#FFFFFF')
    color = ColorField(default='#FF0000')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EveDoctrine(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(populate_from="name")
    description = models.TextField()
    tags = models.ManyToManyField('EveDoctrineTag', blank=True)
    fittings = models.ManyToManyField('EveFitting', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    composition = models.TextField()
    active = models.BooleanField(default=True)
    primary = models.BooleanField(default=False)
    universal = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class EveFitting(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(populate_from="name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()

    # important for integrations
    ship_name = models.CharField(max_length=255)
    ship_type_id = models.IntegerField()
    ship_type_name = models.CharField(max_length=255)

    # fitting info
    eft_format = models.TextField()
    multibuy_format = models.TextField(null=True, blank=True)
    latest_price = models.DecimalField(max_digits=36, decimal_places=2, default=0.00)

    # in-game fitting tracking
    latest_version = models.CharField(max_length=255)
    build_updated = models.BooleanField(default=False)
    fl33t_updated = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)

    # aliases for legacy fittings, comma separated
    legacy_aliases = models.CharField(max_length=255, null=True, blank=True)

    @property
    def image(self):
        return "https://image.eveonline.com/Render/%s_256.png" % self.ship_type_id
    
    @property
    def wheel(self):
        from .schemas import FittingWheelResponse
        return FittingWheelResponse(29344, low_slots=[10190, 10190])
    def __str__(self):
        return self.name
    
class EsiFleet(models.Model):
    id = models.BigIntegerField(primary_key=True) # esi representation
    fleet = models.OneToOneField('EveFleet', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_free_move = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)
    is_voice_enabled = models.BooleanField(default=False)
    motd = models.TextField(null=True, blank=True)

    @property
    def active(self):
        return self.end_time is None

class EsiFleetMember(models.Model):
    fleet = models.ForeignKey('EsiFleet', on_delete=models.CASCADE)
    character_id = models.BigIntegerField()
    join_time = models.DateTimeField()
    role = models.CharField(max_length=255)
    role_name = models.CharField(max_length=255)
    ship_type_id = models.BigIntegerField()
    solar_system_id = models.BigIntegerField()
    squad_id = models.BigIntegerField()
    station_id = models.BigIntegerField(null=True, blank=True)
    takes_fleet_warp = models.BooleanField(default=False)
    wing_id = models.BigIntegerField()

    # human readable values 
    character_name = models.CharField(max_length=255, null=True, blank=True)
    ship_name = models.CharField(max_length=255, null=True, blank=True)
    solar_system_name = models.CharField(max_length=255, null=True, blank=True)

    # fleet and character_id are unique together
    class Meta:
        unique_together = ('fleet', 'character_id')

class EsiFleetMemberTrackingLog(models.Model):
    esi_fleet_member = models.ForeignKey('EsiFleetMember', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    ship_type_id = models.BigIntegerField()
    solar_system_id = models.BigIntegerField()
    station_id = models.BigIntegerField(null=True, blank=True)

    # human readable values
    ship_name = models.CharField(max_length=255, null=True, blank=True)
    solar_system_name = models.CharField(max_length=255, null=True, blank=True)
