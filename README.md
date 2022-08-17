[![Web !](https://img.shields.io/badge/Web-Read%20us%20more-green)](https://resilienceacademy.ac.tz/contact-us/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Twitter follow:](https://img.shields.io/twitter/url?url=https%3A%2F%2Ftwitter.com%2FTanzania_RA)](https://twitter.com/Tanzania_RA)

# Resilience Academy documentation
This is a documentation on how to install our Climate Risk Database (CRD) to your own servers. This documentation is based on the step by step procedures which was used to create Resilience Academy 
=======
This is a documentation on how to install our `Climate Risk Database (CRD)` to your own servers. This documentation is based on the step by step procedures which was used to create the `CRD`  

The `CRD` is one of the Resilience Academy service that was established to facilitate access of spatial and non spatial data from the Resilience Academy innitiatives. The data in the `CRD` involves the geospatial data (vector data and raster data) and the reports that have been produced from the Tanzania Urban Resilience Progra (TURP). More information about TURP can be accessed [here](worldbank.org/en/programs/tanzania-urban-resilience-program)

## License

ProjectSend is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Authors

* **Resilience Academy Experts** - [Cooperation between University partners](https://resilienceacademy.ac.tz/)

## Contact us

If you would like to contact us, send an email throught: resilienceacademytz@gmail.com
>>>>>>> b708934110ebd67c9df01454a15e79ba0bec7523


## Table of Contents

-  [Setup](#Setup)
-  [Build](#Build)
-  [Customize](#Customize)

GeoNode-Project Template for `resilienceacademy`

## Setup

1. Clone the git repository.

    ```bash
    cd /opt
    git clone https://github.com/geosolutions-it/resilienceacademy.git
    ```

2. Move to repo folder.

    ```bash
    cd /opt/resilienceacademy
    ```

3. Customize the environment.

    a) `django.env`

      ```bash
      nano scripts/docker/env/production/django.env
      ```

      ```diff
      --- a/scripts/docker/env/production/django.env
      +++ b/scripts/docker/env/production/django.env
      @@ -3,20 +3,20 @@ GEONODE_INSTANCE_NAME=geonode
      DOCKER_ENV=production
      UWSGI_CMD=uwsgi --ini /usr/src/resilienceacademy/uwsgi.ini
      
      -SITEURL=https://geonode-06.utu.fi/
      +SITEURL=https://<public host>/
      ALLOWED_HOSTS=['django', '*']
      
      -GEONODE_LB_HOST_IP=geonode-06.utu.fi
      +GEONODE_LB_HOST_IP=<public host>
      # port where the server can be reached on HTTP
      # GEONODE_LB_PORT=80
      # port where the server can be reached on HTTPS
      GEONODE_LB_PORT=443
      
      -ADMIN_PASSWORD=admin
      +ADMIN_PASSWORD=<your admin pwd>
      -ADMIN_EMAIL=admin@geonode-06.utu.fi
      +ADMIN_EMAIL=<your admin email>
      
      -GEOSERVER_WEB_UI_LOCATION=https://geonode-06.utu.fi/geoserver/
      -GEOSERVER_PUBLIC_LOCATION=https://geonode-06.utu.fi/geoserver/
      +GEOSERVER_WEB_UI_LOCATION=https://<public host>/geoserver/
      +GEOSERVER_PUBLIC_LOCATION=https://<public host>/geoserver/
      GEOSERVER_LOCATION=http://geoserver:8080/geoserver/
      
      @@ -39,7 +39,7 @@ MOSAIC_ENABLED=False
      BROKER_URL=amqp://guest:guest@rabbitmq:5672/
      MONITORING_ENABLED=True
      MODIFY_TOPICCATEGORY=True
      -
      +AVATAR_GRAVATAR_SSL=True
      EXIF_ENABLED=False
      CREATE_LAYER=False
      FAVORITE_ENABLED=False
      ```

    b) `geoserver.env`

      ```bash
      nano scripts/docker/env/production/geoserver.env
      ```

      ```diff
      --- a/scripts/docker/env/production/geoserver.env
      +++ b/scripts/docker/env/production/geoserver.env
      @@ -1,6 +1,6 @@
      DOCKER_HOST_IP
      
      -GEONODE_LB_HOST_IP=geonode-06.utu.fi
      +GEONODE_LB_HOST_IP=<public host>
      # port where the server can be reached on HTTP
      # GEONODE_LB_PORT=80
      # port where the server can be reached on HTTPS
      ```

    c) `nginx.env`

      ```bash
      nano scripts/docker/env/production/nginx.env
      ```

      ```diff
      --- a/scripts/docker/env/production/nginx.env
      +++ b/scripts/docker/env/production/nginx.env
      @@ -1,12 +1,12 @@
      
      -ADMIN_EMAIL=admin@geonode-06.utu.fi
      +ADMIN_EMAIL=<your admin email>
      
      # IP or domain name and port where the server can be reached on HTTP (leave HOST empty if you want to use HTTPS only)
      HTTP_HOST=
      HTTP_PORT=80
      
      # IP or domain name and port where the server can be reached on HTTPS (leave HOST empty if you want to use HTTP only)
      -HTTPS_HOST=geonode-06.utu.fi
      +HTTPS_HOST=<public host>
      HTTPS_PORT=443
      
      # Let's Encrypt certificates for https encryption. You must have a domain name as HTTPS_HOST (doesn't work
      @@ -15,6 +15,6 @@ HTTPS_PORT=443
      # staging : we get staging certificates (are invalid, but allow to test the process completely and have much higher limit rates)
      # production : we get a normal certificate (default)
      #LETSENCRYPT_MODE=disabled
      -LETSENCRYPT_MODE=staging
      +LETSENCRYPT_MODE=production
      
      RESOLVER=127.0.0.11
      ```

## Build

1. Double check `docker-compose.yml` and `docker-compose.override.yml` are correctly configured.

2. Run the docker compose build.


    ```bash
    cd /opt/resilienceacademy
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
    git clone https://github.com/geosolutions-it/geonode-customisation.git
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
