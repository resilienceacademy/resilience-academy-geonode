# Resilienceacademy3

## Table of Contents

-  [Setup](#Setup)
-  [Build](#Build)
-  [Customize](#Customize)

GeoNode-Project Template for `resilienceacademy`

## Setup

1. Clone the git repository.

    ```bash
    cd /opt
    git clone https://github.com/geosolutions-it/resilienceacademy.git -b resilienceacademy3
    ```

2. Move to repo folder.

    ```bash
    cd /opt/resilienceacademy3
    ```

3. Customize the environment.

    `.env`

      ```bash
      nano .env
      ```
      
      Change all occurrencies of `https://geonode.resilienceacademy.ac.tz` with your final host name.
      
      Update the other variables as follows:
      
      ```diff
      diff --git a/.env b/.env
      index 12db1c7..78efb4f 100644
      --- a/.env
      +++ b/.env
      @@ -43,7 +43,7 @@ GEOSERVER_WEB_UI_LOCATION=https://geonode.resilienceacademy.ac.tz/geoserver/
       GEOSERVER_PUBLIC_LOCATION=https://geonode.resilienceacademy.ac.tz/geoserver/
       GEOSERVER_LOCATION=http://geoserver:8080/geoserver/
       GEOSERVER_ADMIN_USER=admin
      -GEOSERVER_ADMIN_PASSWORD=geoserver
      +GEOSERVER_ADMIN_PASSWORD=<your_geoserver_admin_password>

       OGC_REQUEST_TIMEOUT=30
       OGC_REQUEST_MAX_RETRIES=1
      @@ -99,8 +99,8 @@ RESOLVER=127.0.0.11
       # #################
       # Admin Settings
       ADMIN_USERNAME=admin
      -ADMIN_PASSWORD=admin
      -ADMIN_EMAIL=no-reply@utu.fi
      +ADMIN_PASSWORD=<your_geonode_admin_password>
      +ADMIN_EMAIL=admin@geonode.resilienceacademy.ac.tz

       # EMAIL Notifications
       EMAIL_ENABLE=False
      @@ -130,16 +130,16 @@ ACCOUNT_EMAIL_VERIFICATION=none
       ACCOUNT_EMAIL_CONFIRMATION_EMAIL=False
       ACCOUNT_EMAIL_CONFIRMATION_REQUIRED=False
       ACCOUNT_AUTHENTICATION_METHOD=username_email
      -AUTO_ASSIGN_REGISTERED_MEMBERS_TO_REGISTERED_MEMBERS_GROUP_NAME=False
      +AUTO_ASSIGN_REGISTERED_MEMBERS_TO_REGISTERED_MEMBERS_GROUP_NAME=True

       # OAuth2
      -OAUTH2_API_KEY=
      -OAUTH2_CLIENT_ID=Jrchz2oPY3akmzndmgUTYrs9gczlgoV20YPSvqaV
      -OAUTH2_CLIENT_SECRET=rCnp5txobUo83EpQEblM8fVj3QT5zb5qRfxNsuPzCqZaiRyIoxM4jdgMiZKFfePBHYXCLd7B8NlkfDBY9HKeIQPcy5Cp08KQNpRHQbjpLItDHv12GvkSeXp6OxaUETv3
      +OAUTH2_API_KEY=
      +OAUTH2_CLIENT_ID=<your_new_oauth2_cliend_id>
      +OAUTH2_CLIENT_SECRET=<your_new_oauth2_cliend_secret>

       # GeoNode APIs
       API_LOCKDOWN=False
      -TASTYPIE_APIKEY=
      +TASTYPIE_APIKEY=<your_new_oauth2_tastypie_key>

       # #################
       # Production and
      @@ -201,3 +201,4 @@ ADMIN_MODERATE_UPLOADS=True
       # Other Apps
       BLOG_BASE_URL=https://resilienceacademy.ac.tz/
       # BLOG_BASE_URL=https://suza.ac.tz/
      +
      ```

## Build

1. Double check `docker-compose.yml` and `docker-compose.override.yml` are correctly configured.

2. Run the docker compose build.


    ```bash
    cd /opt/resilienceacademy3
    ./docker-build-sh
    ```

3. Follow the logs in order to be sure the container started up correctly.

    ```bash
    docker-compose logs -f django
    ```

    Wait until you see:

    ```bash
    ...
    django4resilienceacademy | got command ${cmd}
    django4resilienceacademy | [uWSGI] getting INI configuration from /usr/src/resilienceacademy/uwsgi.ini
    ```

4. Check the GeoNode has correctly started up.

    ```bash
    # Browse to
    https://<public host>/
    ```

## Customize

1. Clone the git repository.

    ```bash
    cd /opt
    git clone https://github.com/resilienceacademy/geonode-customisation.git -b resilienceacademy3
    ```

2. Move to repo folder.

    ```bash
    cd /opt/geonode-customisation
    ```

3. Make .sh files executable.

    ```bash
    chmod u+x *.sh
    ```

4. Execute `update.sh`.

    ```bash
    ./update.sh
    ```

`update.sh` will always pull latest version from git before updating files. All files will be backed up before updating. Process halts on error.
