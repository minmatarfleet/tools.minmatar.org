from enum import unique
from django.db import models

STRUCTURE_TYPES = (
    ("astrahus", "Astrahus"),
    ("fortizar", "Fortizar"),
    ("keepstar", "Keepstar"),
    ("raitaru", "Raitaru"),
    ("azbel", "Azbel"),
    ("sotiyo", "Sotiyo"),
    ("athanor", "Athanor"),
    ("tatara", "Tatara"),
)


# Create your models here.
class StructureIntel(models.Model):
    structure_types = STRUCTURE_TYPES + (
        ("ansiblex", "Ansiblex Jump Gate"),
        ("pharolux", "Pharolux Cyno Beacon"),
    )
    structure_name = models.CharField(max_length=255)
    structure_type = models.CharField(max_length=255, choices=structure_types)
    structure_type_id = models.BigIntegerField()
    system = models.CharField(max_length=255)
    system_id = models.BigIntegerField(null=True, blank=True)
    constellation = models.CharField(max_length=255, null=True, blank=True)
    constellation_id = models.BigIntegerField(null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    region_id = models.BigIntegerField(null=True, blank=True)
    corporation_name = models.CharField(max_length=255)
    corporation_id = models.BigIntegerField()
    alliance_name = models.CharField(max_length=255, null=True, blank=True)
    alliance_id = models.BigIntegerField(null=True, blank=True)
    related_alliance_name = models.CharField(max_length=255, null=True, blank=True)
    related_alliance_id = models.BigIntegerField(null=True, blank=True)
    timer = models.CharField(max_length=5)
    fitting = models.TextField()

    # audit
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_character_id = models.BigIntegerField()
    created_by_character_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('system', 'structure_name')

class StructureIntelCampaign(models.Model):
    status_types = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("complete", "Complete"),
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=255, choices=status_types, default="active")

    # Parameters
    system = models.CharField(max_length=255, null=True, blank=True)
    constellation = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    corporation_name = models.CharField(max_length=255, null=True, blank=True)
    alliance_name = models.CharField(max_length=255, null=True, blank=True)
    related_alliance_name = models.CharField(max_length=255, null=True, blank=True)
    price_per_structure = models.IntegerField(default=0)


    # Results
    structures = models.ManyToManyField(StructureIntel, blank=True)

    def __str__(self):
        return self.name

class StructureTimer(models.Model):
    structure_types = STRUCTURE_TYPES
    structure_name = models.CharField(max_length=255)
    structure_type = models.CharField(max_length=255, choices=structure_types)
    structure_type_id = models.BigIntegerField()

    alliance_name = models.CharField(max_length=255)
    alliance_id = models.BigIntegerField()

    timer_types = (("armor", "Armor"), ("structure", "Structure"))
    timer_type = models.CharField(max_length=255, choices=timer_types)
    timer = models.DateTimeField()

    system = models.CharField(max_length=255)
    system_id = models.BigIntegerField(null=True, blank=True)
    constellation = models.CharField(max_length=255, null=True, blank=True)
    constellation_id = models.BigIntegerField(null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    region_id = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by_character_id = models.BigIntegerField()
    created_by_character_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.structure_name} - {self.timer_type} timer - {self.timer.strftime('%Y-%m-%dT%H:%M')}"
