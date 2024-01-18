from django.contrib import admin
from .models import StructureIntel, StructureIntelCampaign, StructureTimer

# Register your models here.
admin.site.register(StructureIntel)
admin.site.register(StructureIntelCampaign)
admin.site.register(StructureTimer)
