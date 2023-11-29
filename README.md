# tools.minmatar.org

# quickstart
1. Use `requirements.txt` to create a virtualenv (pip, pipenv, whatever)
2. migrate database `python3 manage.py migrate`
3. run `python3 manage.py runserver`

# uses
1. Django
2. Celery
3. Popular third party libraries for ESI and Discord (`django-esi`, `django-eve-auth`, `python-discord-client`)


# production
1. mariadb
2. redis 
3. nginx
4. supervisor 