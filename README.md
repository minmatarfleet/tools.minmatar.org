# tools.minmatar.org

# local development quickstart
1. Setup your `docker-compose.yml` to contain the contents of `docker-compose-local.yml`.
2. Setup your `.env` file based on the `.env.example` file with the information you get from CCP's ESI page (create your own application at: https://developers.eveonline.com/), the username and password you'd like to use for the website database, and the auth database password from BearThatCares.
3. Run `docker compose up -d` to create and start the containers.
4. Run `docker compose exec db mariadb -u root -p` and use the password set in the `docker-compose-local.yml` file under the `MYSQL_ROOT_PASSWORD` section.
5. Create a user in mariadb that will be used by the server: `CREATE USER 'tools'@'%' IDENTIFIED BY 'example';` to create a user with the password 'example'. Make sure this matches what's in your `.env` file.
6. Create the tools database: `CREATE DATABASE tools CHARACTER SET utf8mb4;`.
7. Grant user privileges to that database: `GRANT ALL PRIVILEGES ON tools.* TO 'tools'@'%';` and exit mariadb (`EXIT;`).
8. Run `docker compose exec app python3 manage.py migrate`. This creates all the tables in the database for you.
9. Navigate to http://localhost:8000 and you should see the website.

This isn't a super quick quickstart and we're still working on streamlining it. If you have issues reach out to the technology team and we'll do our best to help.

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