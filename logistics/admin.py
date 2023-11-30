from django.contrib import admin
from .models import EveCourierEntity, EveCourierPilot, EsiCourierEntityResponse, FreightRoute
# Register your models here.
admin.site.register(EveCourierEntity)
admin.site.register(EveCourierPilot)
admin.site.register(EsiCourierEntityResponse)
admin.site.register(FreightRoute)