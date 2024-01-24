"""Authorize characters based on allianceauth roles (RBAC)"""
from django.shortcuts import redirect
from django.db import connections
from django.contrib import messages
from django.db.utils import ConnectionDoesNotExist
from django.conf import settings


def get_main_character_id(character_id):
    query = """
    SELECT ac.user_id, ee.character_id, ee.character_name, (
    select ee.character_id from eveonline_evecharacter ee where id = ap.main_character_id
    ) as main_character_id
    from eveonline_evecharacter ee
    join authentication_characterownership ac on ac.character_id = ee.id
    join authentication_userprofile ap on ac.user_id = ap.user_id
    where ee.character_id = %s
    """
    with connections["allianceauth"].cursor() as cursor:
        cursor.execute(query, [character_id])
        result = cursor.fetchone()
        if result[3] != character_id:
            return result[3]
        else:
            return None


def character_id_has_roles(character_id, roles):
    try:
        with connections["allianceauth"].cursor() as cursor:
            query = """
            WITH characters AS (
                SELECT ac.user_id, ee.character_id, ee.character_name
                from eveonline_evecharacter ee
                join authentication_characterownership ac on ac.character_id = ee.id
            ),
            user_groups as (
                SELECT aug.user_id, ag.name
                from auth_user_groups aug
                join auth_group ag on ag.id = aug.group_id
            ),
            user_states as (
                select aup.user_id, ast.name
                from authentication_userprofile aup
                join authentication_state ast on ast.id = aup.state_id
            )
            SELECT characters.user_id, user_groups.name, user_states.name
            FROM characters
            LEFT JOIN user_groups ON user_groups.user_id = characters.user_id
            LEFT JOIN user_states ON user_states.user_id = characters.user_id
            WHERE characters.character_id=%s
            AND (user_groups.name IN %s OR user_states.name IN %s);
            """
            # fetch 'id' from discord_discorduser where uid = discord_id
            cursor.execute(query, [character_id, roles, roles])
            result = cursor.fetchone()
            print(result)
            return result is not None
    except ConnectionDoesNotExist:
        if settings.DEBUG:
            return True


# write a decorator that checks if the request.user.eve_character has the required roles
def required_roles(roles=[], redirect_url="home"):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if character_id_has_roles(request.user.eve_character.character_id, roles):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request, "You do not have the required roles to access that page."
                )
                return redirect(redirect_url)

        return _wrapped_view

    return decorator
