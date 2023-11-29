from django.contrib import admin
from .models import (
    EveFleet, 
    EveDoctrine, 
    EveFitting, 
    EveDoctrineTag, EveFleetDiscordWebhook, EveFleetDiscordNotification, EsiFleet, EsiFleetMember, EsiFleetMemberTrackingLog,
    EveFleetMOTDTemplate
)
# Register your models here.
admin.site.register(EveFleet)
admin.site.register(EveFleetDiscordWebhook)
admin.site.register(EveFleetDiscordNotification)
admin.site.register(EveDoctrine)
admin.site.register(EveDoctrineTag)
admin.site.register(EsiFleet)
admin.site.register(EsiFleetMember)
admin.site.register(EsiFleetMemberTrackingLog)
admin.site.register(EveFleetMOTDTemplate)

@admin.register(EveFitting)
class EveFittingAdmin(admin.ModelAdmin):
    ordering = ["name"]
