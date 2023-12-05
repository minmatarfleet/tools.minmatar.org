# tools.minmatar.org

# local development quickstart
1. Copy the contents of `docker-compose-local.yml` into `docker-compose.yml`
2. Setup your `.env` file based on the `.env.example` file
  - Create an application [here](https://developers.eveonline.com/) with CCP and get the ESI Client ID and ESI Secret Key
  - By default the database user passwords are `example` for users `root` and `tools`, if you'd like this to be different update the relevant sections in `.env`, `docker-compose.yml`, and `dev/mariadb/setup.sql`
  - Get the auth database password from BearThatCares
3. Run `docker compose up -d` to create and start the containers. In the background this sets up the needed database users and database.
4. Run `docker compose exec app python3 manage.py migrate`. This creates all the tables in the database for you.
5. Navigate to http://localhost:8000 and you should see the website.

This isn't a perfect setup and we're still working on streamlining it. If you have issues reach out to the technology team and we'll do our best to help.
Once you set this up once it will keep your db setup between development instances and you will only need to migrate if you change the database structure.

# uses
1. Django
2. Celery
3. Docker
4. Popular third party libraries for ESI and Discord (`django-esi`, `django-eve-auth`, `python-discord-client`)

# production
1. mariadb
2. redis 
3. nginx
4. supervisor 