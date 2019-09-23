import ast
import json
import logging
import os
import re
import time
import datetime
import docker
import socket

from urlparse import urlparse
from invoke import run, task

BOOTSTRAP_IMAGE_CHEIP = 'codenvy/che-ip:nightly'


@task
def waitfordbs(ctx):
    print "**************************databases*******************************"
    ctx.run("/usr/bin/wait-for-databases {0}".format('db'), pty=True)


@task
def waitforgeoserver(ctx):
    print "****************************geoserver********************************"
    while not _rest_api_availability(os.environ['GEOSERVER_LOCATION'] + 'rest'):
        print ("Wait for GeoServer API availability...")
    print "GeoServer is available for HTTP calls!"


@task
def update(ctx):
    print "***************************setting env*********************************"
    ctx.run("env", pty=True)
    pub_ip = _geonode_public_host_ip()
    print "Public Hostname or IP is {0}".format(pub_ip)
    pub_port = _geonode_public_port()
    print "Public PORT is {0}".format(pub_port)
    db_url = _update_db_connstring()
    geodb_url = _update_geodb_connstring()
    service_ready = False
    while not service_ready:
        try:
            socket.gethostbyname('geonode')
            service_ready = True
        except BaseException:
            time.sleep(10)

    override_env = "$HOME/.override_env"
    if os.path.exists(override_env):
        os.remove(override_env)
    else:
        print("Can not delete the %s file as it doesn't exists" % override_env)

    envs = {
        "local_settings": "{0}".format(_localsettings()),
        "siteurl": os.environ.get('SITEURL',
                                  'http://{0}:{1}/'.format(pub_ip, pub_port) if pub_port else 'http://{0}/'.format(pub_ip)),
        "geonode_docker_host": "{0}".format(socket.gethostbyname('geonode')),
        "public_fqdn": "{0}:{1}".format(pub_ip, pub_port),
        "public_host": "{0}".format(pub_ip),
        "dburl": db_url,
        "geodburl": geodb_url,
        "monitoring": os.environ.get('MONITORING_ENABLED', False),
        "monitoring_data_ttl": os.environ.get('MONITORING_DATA_TTL', 7),
        "gs_pub_loc": os.environ.get('GEOSERVER_PUBLIC_LOCATION',
                                     'http://{0}:{1}/geoserver/'.format(pub_ip, pub_port) if pub_port else 'http://{0}/geoserver/'.format(pub_ip)),
        "gs_admin_pwd": os.environ.get('GEOSERVER_ADMIN_PASSWORD', 'geoserver'),
        "override_fn": override_env
    }
    try:
        current_allowed = ast.literal_eval(os.getenv('ALLOWED_HOSTS') or \
                                           "['{public_fqdn}', '{public_host}', 'localhost', 'django', 'resilienceacademy',]".format(**envs))
    except ValueError:
        current_allowed = []
    current_allowed.extend(['{}'.format(pub_ip), '{}:{}'.format(pub_ip, pub_port)])
    allowed_hosts = ['"{}"'.format(c) for c in current_allowed] + ['"geonode"', '"django"']

    ctx.run("echo export DJANGO_SETTINGS_MODULE=\
{local_settings} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export MONITORING_ENABLED=\
{monitoring} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export MONITORING_HOST_NAME=\
{geonode_docker_host} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export MONITORING_SERVICE_NAME=\
local-geonode >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export MONITORING_DATA_TTL=\
{monitoring_data_ttl} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export GEOSERVER_PUBLIC_LOCATION=\
{gs_pub_loc} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export GEOSERVER_ADMIN_PASSWORD=\
{gs_admin_pwd} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export SITEURL=\
{siteurl} >> {override_fn}".format(**envs), pty=True)
    ctx.run('echo export ALLOWED_HOSTS="\\"{}\\"" >> {override_fn}'.format(
        allowed_hosts, **envs), pty=True)
    if not os.environ.get('DATABASE_URL'):
        ctx.run("echo export DATABASE_URL=\
{dburl} >> {override_fn}".format(**envs), pty=True)
    if not os.environ.get('GEODATABASE_URL'):
        ctx.run("echo export GEODATABASE_URL=\
{geodburl} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export LOGIN_URL=\
{siteurl}account/login/ >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export LOGOUT_URL=\
{siteurl}account/logout/ >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export LOGIN_REDIRECT_URL=\
{siteurl} >> {override_fn}".format(**envs), pty=True)
    ctx.run("echo export LOGOUT_REDIRECT_URL=\
{siteurl} >> {override_fn}".format(**envs), pty=True)
    ctx.run("source %s" % override_env, pty=True)
    print "****************************finalize env**********************************"
    ctx.run("env", pty=True)


@task
def migrations(ctx):
    print "**************************migrations*******************************"
    ctx.run("python manage.py makemigrations --noinput --merge --settings={0}".format(
        _localsettings()
    ), pty=True)
    ctx.run("python manage.py makemigrations --noinput --settings={0}".format(
        _localsettings()
    ), pty=True)
    ctx.run("python manage.py migrate --noinput --settings={0}".format(
        _localsettings()
    ), pty=True)
    ctx.run("python manage.py updategeoip --settings={0}".format(
        _localsettings()
    ), pty=True)
    try:
        ctx.run("python manage.py rebuild_index --noinput --settings={0}".format(
            _localsettings()
        ), pty=True)
    except:
        pass

@task
def statics(ctx):
    print "**************************statics*******************************"
    ctx.run('mkdir -p /mnt/volumes/statics/{static,uploads}')
    ctx.run("python manage.py collectstatic --noinput --clear --settings={0}".format(
        _localsettings()
    ), pty=True)

@task
def prepare(ctx):
    print "**********************prepare fixture***************************"
    ctx.run("rm -rf /tmp/default_oauth_apps_docker.json", pty=True)
    _prepare_oauth_fixture()


@task
def fixtures(ctx):
    print "**************************fixtures********************************"
    ctx.run("python manage.py loaddata sample_admin \
--settings={0}".format(_localsettings()), pty=True)
    ctx.run("python manage.py loaddata /tmp/default_oauth_apps_docker.json \
--settings={0}".format(_localsettings()), pty=True)
    ctx.run("python manage.py loaddata /usr/src/resilienceacademy/fixtures/initial_data.json \
--settings={0}".format(_localsettings()), pty=True)
    ctx.run("python manage.py set_all_layers_alternate \
--settings={0}".format(_localsettings()), pty=True)

@task
def collectstatic(ctx):
    print "************************static artifacts******************************"
    ctx.run("django-admin.py collectstatic --noinput \
--settings={0}".format(_localsettings()), pty=True)


@task
def geoserverfixture(ctx):
    print "********************geoserver fixture********************************"
    _geoserver_info_provision(os.environ['GEOSERVER_LOCATION'] + "rest/")


@task
def monitoringfixture(ctx):
    print "*******************monitoring fixture********************************"
    ctx.run("rm -rf /tmp/default_monitoring_apps_docker.json", pty=True)
    _prepare_monitoring_fixture()
    ctx.run("django-admin.py loaddata /tmp/default_monitoring_apps_docker.json \
--settings={0}".format(_localsettings()), pty=True)


@task
def updategeoip(ctx):
    print "**************************update geoip*******************************"
    ctx.run("django-admin.py updategeoip \
    --settings={0}".format(_localsettings()), pty=True)


@task
def updateadmin(ctx):
    print "***********************update admin details**************************"
    ctx.run("rm -rf /tmp/django_admin_docker.json", pty=True)
    _prepare_admin_fixture(os.environ.get('ADMIN_PASSWORD', 'admin'), os.environ.get('ADMIN_EMAIL', 'admin@example.org'))
    ctx.run("django-admin.py loaddata /tmp/django_admin_docker.json \
--settings={0}".format(_localsettings()), pty=True)


@task
def collectmetrics(ctx):
    print "************************collect metrics******************************"
    ctx.run("python -W ignore manage.py collect_metrics  \
    --settings={0} -n -t xml".format(_localsettings()), pty=True)

@task
def initialized(ctx):
    print "**************************init file********************************"
    ctx.run('date > /mnt/volumes/statics/geonode_init.lock')

def _docker_host_ip():
    client = docker.from_env()
    ip_list = client.containers.run(BOOTSTRAP_IMAGE_CHEIP,
                                    network_mode='host'
                                    ).split("\n")
    if len(ip_list) > 1:
        print("Docker daemon is running on more than one \
address {0}".format(ip_list))
        print("Only the first address:{0} will be returned!".format(
            ip_list[0]
        ))
    else:
        print("Docker daemon is running at the following \
address {0}".format(ip_list[0]))
    return ip_list[0]


def _container_exposed_port(component, instname):
    client = docker.from_env()
    ports_dict = json.dumps(
        [c.attrs['Config']['ExposedPorts'] for c in client.containers.list(
            filters={
                'label': 'org.geonode.component={0}'.format(component),
                'status': 'running'
            }
        ) if '{0}'.format(instname) in c.name][0]
    )
    for key in json.loads(ports_dict):
        port = re.split('/tcp', key)[0]
    return port

def _update_db_connstring():
    user = os.getenv('GEONODE_DATABASE', 'geonode')
    pwd = os.getenv('GEONODE_DATABASE_PASSWORD', 'geonode')
    dbname = os.getenv('GEONODE_DATABASE', 'geonode')
    connstr = 'postgres://{0}:{1}@db:5432/{2}'.format(
        user,
        pwd,
        dbname
    )
    return connstr


def _update_geodb_connstring():
    geouser = os.getenv('GEONODE_GEODATABASE', 'geonode_data')
    geopwd = os.getenv('GEONODE_GEODATABASE_PASSWORD', 'geonode_data')
    geodbname = os.getenv('GEONODE_GEODATABASE', 'geonode_data')
    geoconnstr = 'postgis://{0}:{1}@db:5432/{2}'.format(
        geouser,
        geopwd,
        geodbname
    )
    return geoconnstr


def _localsettings():
    settings = os.getenv('DJANGO_SETTINGS_MODULE', 'resilienceacademy.settings')
    return settings


def _rest_api_availability(url):
    import requests
    try:
        r = requests.request('get', url, verify=False)
        r.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print "GeoServer connection error is {0}".format(e)
        return False
    except requests.exceptions.HTTPError as er:
        print "GeoServer HTTP error is {0}".format(er)
        return False
    else:
        print "GeoServer API are available!"
        return True


def _geonode_public_host_ip():
    gn_pub_hostip = os.getenv('GEONODE_LB_HOST_IP', None)
    if not gn_pub_hostip:
        gn_pub_hostip = _docker_host_ip()
    return gn_pub_hostip


def _geonode_public_port():
    gn_pub_port = os.getenv('GEONODE_LB_PORT', '')
    if not gn_pub_port:
        gn_pub_port = _container_exposed_port(
            'nginx',
            os.getenv('GEONODE_INSTANCE_NAME', 'starterkit')
        )
    elif gn_pub_port in ('80', '443'):
        gn_pub_port = None
    return gn_pub_port


def _prepare_oauth_fixture():
    upurl = urlparse(os.environ['SITEURL'])
    net_scheme = upurl.scheme
    pub_ip = _geonode_public_host_ip()
    print "Public Hostname or IP is {0}".format(pub_ip)
    pub_port = _geonode_public_port()
    print "Public PORT is {0}".format(pub_port)
    default_fixture = [
        {
            "model": "oauth2_provider.application",
            "pk": 1001,
            "fields": {
                "skip_authorization": True,
                "created": "2018-05-31T10:00:31.661Z",
                "updated": "2018-05-31T11:30:31.245Z",
                "algorithm": "RS256",
                "redirect_uris": "{0}://{1}:{2}/geoserver/index.html".format(net_scheme, pub_ip, pub_port) if pub_port else "{0}://{1}/geoserver/index.html".format(net_scheme, pub_ip),
                "name": "GeoServer",
                "authorization_grant_type": "authorization-code",
                "client_type": "confidential",
                "client_id": "Jrchz2oPY3akmzndmgUTYrs9gczlgoV20YPSvqaV",
                "client_secret": "\
rCnp5txobUo83EpQEblM8fVj3QT5zb5qRfxNsuPzCqZaiRyIoxM4jdgMiZKFfePBHYXCLd7B8NlkfDB\
Y9HKeIQPcy5Cp08KQNpRHQbjpLItDHv12GvkSeXp6OxaUETv3",
                "user": [
                    "admin"
                ]
            }
        }
    ]
    with open('/tmp/default_oauth_apps_docker.json', 'w') as fixturefile:
        json.dump(default_fixture, fixturefile)

def _prepare_monitoring_fixture():
    upurl = urlparse(os.environ['SITEURL'])
    net_scheme = upurl.scheme
    pub_ip = _geonode_public_host_ip()
    print "Public Hostname or IP is {0}".format(pub_ip)
    pub_port = _geonode_public_port()
    print "Public PORT is {0}".format(pub_port)
    #d = str(datetime.datetime.now())
    d = '1970-01-01 00:00:00'
    default_fixture = [
        {
            "fields": {
                "active": True,
                "ip": "{0}".format(os.environ['MONITORING_HOST_NAME']),
                "name": "geonode"
            },
            "model": "monitoring.host",
            "pk": 1
        },
        {
            "fields": {
                "name": "local-geonode",
                "url": "{0}://{1}/".format(net_scheme, os.environ['MONITORING_HOST_NAME']),
                "notes": "",
                "last_check": d,
                "active": True,
                "host": 1,
                "check_interval": "00:01:00",
                "service_type": 1
            },
            "model": "monitoring.service",
            "pk": 1
        },
        {
            "fields": {
                "name": "localhost-hostgeonode",
                "url": "{0}://{1}/".format(net_scheme, os.environ['MONITORING_HOST_NAME']),
                "notes": "",
                "last_check": d,
                "active": True,
                "host": 1,
                "check_interval": "00:01:00",
                "service_type": 3
            },
            "model": "monitoring.service",
            "pk": 2
        },
        {
            "fields": {
                "name": "localhost-hostgeoserver",
                "url": "{0}://{1}/geoserver/".format(net_scheme, os.environ['MONITORING_HOST_NAME']),
                "notes": "",
                "last_check": d,
                "active": True,
                "host": 1,
                "check_interval": "00:01:00",
                "service_type": 4
            },
            "model": "monitoring.service",
            "pk": 3
        },
        {
            "fields": {
                "name": "default-geoserver",
                "url": "{0}://{1}/geoserver/".format(net_scheme, os.environ['MONITORING_HOST_NAME']),
                "notes": "",
                "last_check": d,
                "active": True,
                "host": 1,
                "check_interval": "00:01:00",
                "service_type": 2
            },
            "model": "monitoring.service",
            "pk": 4
        }
    ]
    with open('/tmp/default_monitoring_apps_docker.json', 'w') as fixturefile:
        json.dump(default_fixture, fixturefile)


def _prepare_admin_fixture(admin_password, admin_email):
    # from django.contrib.auth import get_user_model
    # admin = get_user_model().objects.get(username="admin")
    # admin.set_password(admin_password)
    # admin.email = admin_email
    # admin.save()
    from django.contrib.auth.hashers import make_password
    d = datetime.datetime.now()
    mdext_date = d.isoformat()[:23] + "Z"
    default_fixture = [
        {
        	"fields": {
        		"date_joined": mdext_date,
        		"email": admin_email,
        		"first_name": "",
        		"groups": [],
        		"is_active": True,
        		"is_staff": True,
        		"is_superuser": True,
        		"last_login": mdext_date,
        		"last_name": "",
        		"password": make_password(admin_password),
        		"user_permissions": [],
        		"username": "admin"
        	},
        	"model": "people.Profile",
        	"pk": 1000
        }
    ]
    with open('/tmp/django_admin_docker.json', 'w') as fixturefile:
        json.dump(default_fixture, fixturefile)
