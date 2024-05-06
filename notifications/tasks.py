from tools.celery  import app 
from discoPy.rest.client import Application, User, Guild, Channel, Stage, Webhook
from django.conf import settings

@app.task()
def bump_forum_posts():
    token = settings.DISCORD_BOT_TOKEN
    channel = Channel(token=token)

    message = "**Forum Post Reminder**\n"
    message += "https://forums.eveonline.com/t/fl33t-up-with-purpose-24-7-small-gang-daily-50-brawls/395819?u=bearthatcares\n"
    message += "https://forums.eveonline.com/t/build-your-future-with-minmatar-industry-mining-hauling/395818?u=bearthatcares\n"
    message += "\n"
    message += "Daily reminder to bump the forum posts. Anyone can do it, but only **once per day**. Please reply with :white_check_mark: or say you got it so that multiple people don't bump."

    channel.create_message(channel_id='1041930035348652112', content=message)

@app.task()
def post_markeedragon_code():
    token = settings.DISCORD_BOT_TOKEN
    channel = Channel(token=token)

    message = "**Buying PLEX on MarkeeDragon?**\n"
    message += "Use code **minmatar** at checkout for 3 percent off!\n"
    message += "http://store.markeedragon.com/affiliate.php?id=992&redirect=index.php?cat=4\n"
    message += "*Markeedragon is an authorized third party retailer of PLEX. https://secure.eveonline.com/thirdpartyretailers*\n"

    channel.create_message(channel_id='1041930035348652112', content=message)