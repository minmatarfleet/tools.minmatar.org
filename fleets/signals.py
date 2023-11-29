from django.db.models import signals
from django.dispatch import receiver  
from .models import EveFleet, EveFleetDiscordNotification, EveFleetDiscordWebhook
from discoPy.rest.client import Application, User, Guild, Channel, Stage, Webhook
from django.conf import settings
from discord_webhook import DiscordWebhook
from .notifications import get_list_of_fleets_notification, get_ping_notification
import requests 
from django.utils import timezone

UPCOMING_CHANNEL_ID = 1174169403873558658
UPCOMING_CHANNEL_MESSAGE_ID = 1174174377311473757

@receiver(signals.post_save, sender=EveFleet) 
def create_fleet(sender, instance, created, **kwargs):
    if created:
        if instance.start_time < timezone.now() + timezone.timedelta(minutes=15):
             EveFleetDiscordNotification.objects.create(type='ping', fleet=instance) 
        else:
            EveFleetDiscordNotification.objects.create(type='created', fleet=instance)

@receiver(signals.post_save, sender=EveFleetDiscordNotification)
def create_fleet_discord_notification(sender, instance, created, **kwargs):
    
    webhooks = EveFleetDiscordWebhook.objects.filter(audience=instance.fleet.audience)
    

    print(instance.type)
    if instance.type == 'ping':
        payload = get_ping_notification(instance.fleet)
        print(created)
        if created:
            for webhook in webhooks:
                print("pinging " + webhook.name)
                requests.post(webhook.webhook_url, json=payload)
    else:
        token = settings.DISCORD_BOT_TOKEN
        # post request to edit message discord api
        payload = get_list_of_fleets_notification()
        requests.patch(
            url=f"https://discord.com/api/v9/channels/{UPCOMING_CHANNEL_ID}/messages/{UPCOMING_CHANNEL_MESSAGE_ID}",
            headers={
                'authorization': f'Bot {token}'
            },
            json=payload
        )

        # post a dummy message
        response = requests.post(
            url=f"https://discord.com/api/v9/channels/{UPCOMING_CHANNEL_ID}/messages",
            headers={
                'authorization': f'Bot {token}'
            },
            json={'content': 'Upcoming fleets updated, this message will be deleted.'}
        )

        # delete message created from above
        response = requests.delete(
            url=f"https://discord.com/api/v9/channels/{UPCOMING_CHANNEL_ID}/messages/{response.json()['id']}",
            headers={
                'authorization': f'Bot {token}'
            },
        )

@receiver(signals.post_delete, sender=EveFleet)
def delete_fleet(sender, instance, **kwargs):
    token = settings.DISCORD_BOT_TOKEN
    # post request to edit message discord api
    payload = get_list_of_fleets_notification()
    requests.patch(
        url=f"https://discord.com/api/v9/channels/{UPCOMING_CHANNEL_ID}/messages/{UPCOMING_CHANNEL_MESSAGE_ID}",
        headers={
            'authorization': f'Bot {token}'
        },
        json=payload
    )