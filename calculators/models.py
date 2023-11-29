from django.db import models

# Create your models here.
class FreightRoute(models.Model):
    origin = models.CharField(max_length=255)
    friendly_origin_name = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    friendly_destination_name = models.CharField(max_length=255)
    
    # standard freight
    jumps = models.IntegerField()
    isk_jump = models.FloatField(default=0)
    jump_freight_required = models.BooleanField(default=False)
    
    # jump freight
    low_risk = models.BooleanField(default=False)
    jump_freight_only = models.BooleanField(default=False)
    jump_freight_capable = models.BooleanField(default=False)
    isk_m3 = models.FloatField(default=0)

    # DEPRECATED
    isotopes = models.IntegerField()
    midpoints = models.IntegerField(default=1)
    

    def __str__(self):
        return self.friendly_origin_name + ' to ' + self.friendly_destination_name