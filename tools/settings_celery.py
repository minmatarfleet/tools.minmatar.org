from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'esi_cleanup_callbackredirect': {
        'task': 'esi.tasks.cleanup_callbackredirect',
        'schedule': crontab(minute=0, hour='*/4'),
    },
    'esi_cleanup_token': {
        'task': 'esi.tasks.cleanup_token',
        'schedule': crontab(minute=0, hour=0),
    },
}

# 0 15 */2 * *
CELERYBEAT_SCHEDULE['notify_bump_forum_posts'] = {
    'task': 'notifications.tasks.bump_forum_posts',
    'schedule': crontab(minute=0, hour=15, day_of_week='*/2'),
}

CELERYBEAT_SCHEDULE['post_markeedragon_code'] = {
    'task': 'notifications.tasks.post_markeedragon_code',
    'schedule': crontab(minute=0, hour=20, day_of_week='monday'),
}

CELERYBEAT_SCHEDULE['update_courier_contracts'] = {
    'task': 'logistics.tasks.update_esi_courier_entity_responses',
    'schedule': crontab(minute=30, hour='*/3'),
}

CELERYBEAT_SCHEDULE['notify_courier_contracts'] = {
    'task': 'logistics.tasks.notify_discord_courier_contracts',
    'schedule': crontab(minute=15, hour='*/12')
}

CELERYBEAT_SCHEDULE['update_fittings'] = {
    'task': 'fleets.tasks.update_fittings',
    'schedule': crontab(minute=30, hour='*/24')
}

CELERYBEAT_SCHEDULE['update_contract_responses'] = {
    'task': 'contracts_v2.tasks.update_esi_corporation_contract_responses',
    'schedule': crontab(minute=20, hour='*/2'),
}

CELERYBEAT_SCHEDULE['create_eve_contracts'] = {
    'task': 'contracts_v2.tasks.create_eve_contracts',
    'schedule': crontab(minute=30, hour='*/2'),
}

# CELERYBEAT_SCHEDULE['notify_contract_entities'] = {
#     'task': 'contracts_v2.tasks.notify_discord_contract_entities',
#     'schedule': crontab(minute=0, hour=20),
# }

CELERYBEAT_SCHEDULE['create_entity_tax_report'] = {
    'task': 'contracts_v2.tasks.create_entity_tax_report',
    'schedule': crontab(0, 0, day_of_month='1'),
}

CELERYBEAT_SCHEDULE['update_esi_fleets'] = {
    'task': 'fleets.tasks.update_esi_fleets',
    # every minute
    'schedule': crontab(minute='*/1'),
}


