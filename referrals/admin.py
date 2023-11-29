from django.contrib import admin
from .models import EveCharacterResourceLink, EveCharacterResourceLinkClick

# Register your models here.
admin.site.register(EveCharacterResourceLink)
admin.site.register(EveCharacterResourceLinkClick)
