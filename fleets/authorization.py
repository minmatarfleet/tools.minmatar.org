"""Authorize characters based on allianceauth roles (RBAC)"""
from django.shortcuts import redirect
from django.db import connections
from django.contrib import messages
from django.db.utils import ConnectionDoesNotExist
from django.conf import settings 


def character_id_has_roles(character_id, roles):
    try:
        with connections['allianceauth'].cursor() as cursor:
            query = """
            SELECT * from CHARACTER_UID_LOOKUP where character_id = %s;
            """
            # fetch 'id' from discord_discorduser where uid = discord_id
            cursor.execute(query, [character_id])
            result = cursor.fetchone()
            if not result:
                return False
            character_id = result[0]
            character_id_roles = result[1].split(',')
            for role in roles:
                if role not in character_id_roles:
                    return False
            return True 
    except ConnectionDoesNotExist:
        if settings.DEBUG:
            return True
    
# write a decorator that checks if the request.user.eve_character has the required roles
def required_roles(roles=[], redirect_url='home'):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if character_id_has_roles(request.user.eve_character.character_id, roles):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You do not have the required roles to access that page.")
                return redirect(redirect_url)
        return _wrapped_view
    return decorator