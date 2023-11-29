from django.db import connections


def get_eve_character_for_discord_username(discord_id):
    with connections['allianceauth'].cursor() as cursor:
        # server owner cannot authorize
        if int(discord_id) == 124039469488799746:
            return "BearThatCares"
        # fetch 'id' from discord_discorduser where uid = discord_id
        cursor.execute("SELECT user_id FROM discord_discorduser WHERE uid = %s", [discord_id])
        user_id = cursor.fetchone()[0]

        cursor.execute("SELECT main_character_id FROM authentication_userprofile WHERE user_id = %s", [user_id])
        main_character_id= cursor.fetchone()[0]

        cursor.execute("SELECT character_name from eveonline_evecharacter WHERE id = %s", [main_character_id])
        character_name = cursor.fetchone()[0]

        return character_name