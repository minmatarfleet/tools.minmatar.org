from django.db import models

# Create your models here.
class EveCharacterResourceLink(models.Model):
    character_id = models.IntegerField()
    resource = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EveCharacterResourceLinkClick(models.Model):
    character_id = models.IntegerField()
    resource_link = models.ForeignKey(EveCharacterResourceLink, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)