# -*- coding: utf-8; mode: python -*-
from milieu import Environment

env = Environment()

from uuid import uuid4
from os.path import join, abspath

LOCAL_PORT = 5000
PORT = env.get_int('PORT', LOCAL_PORT)

# READY TO DEPLOY
DEBUG = PORT is LOCAL_PORT
PRODUCTION = not DEBUG
TESTING = env.get('TESTING', False)

# Database connection URI
DATABASE = env.get('MYSQL_URI')


if not PRODUCTION:
    import os
    DATABASE = env.get('INSTANCES_DB', 'mysql://root@localhost/instances')

# Static assets craziness
LOCAL_FILE = lambda *p: abspath(join(__file__, '..', *p))

SQLALCHEMY_DATABASE_URI = DATABASE

if DEBUG:  # localhost
    HOST = 'localhost'
    DOMAIN = '{0}:{1}'.format(HOST, PORT)
    GITHUB_CLIENT_ID = 'bae76639a0b0be1ba87f'
    GITHUB_CLIENT_SECRET = 'b48f447af184fdcd67e817769c4e309781f7ac6d'
    STATIC_BASE_URL = '/static/'
else:
    HOST = env.get("HOST")
    DOMAIN = env.get("DOMAIN")
    GITHUB_CLIENT_ID = '5ea8d7815912f72daf71'
    GITHUB_CLIENT_SECRET = '8cad784045aa0a99c687abc0da696bf16a3db0a6'
    STATIC_BASE_URL = 'https://static.instanc.es.s3-website-us-east-1.amazonaws.com/static/

SCHEMA = PORT == 443 and 'https://' or "http://"
GITHUB_CALLBACK_URL = '{SCHEMA}{DOMAIN}/.sys/callback'.format(**locals())
print GITHUB_CALLBACK_URL
absurl = lambda *path: "{0}{1}/{2}".format(SCHEMA, DOMAIN, "/".join(path).lstrip('/'))
sslabsurl = lambda *path: "{0}{1}/{2}".format("https://", DOMAIN, "/".join(path).lstrip('/'))

RELEASE = env.get('RELEASE', uuid4().hex)
# Session key, CHANGE IT IF YOU GET TO THE PRODUCTION! :)
SECRET_KEY = RELEASE + '%F&G*&H(*ds3657d468f57g68h'

REDIS_URI = env.get_uri("REDIS_URI")
GRAPHITE_URI = env.get_uri("GRAPHITE_URI", "http://ec2-23-22-195-36.compute-1.amazonaws.com")

GRAPHITE_SERVER_DOMAIN = GRAPHITE_URI.host
AUTH_USER = env.get("AUTH_USER", "")
AUTH_PASSWD = env.get("AUTH_PASSWD", "")
absurl = lambda *path: "{0}{1}/{2}".format(SCHEMA, DOMAIN, "/".join(path).lstrip('/'))
BETA_USERS = [
    'gabrielfalcao',
    'visionmedia',
    'kennethreitz',
    'heynemann',
    'vsanta',
    'felipesilva',
    'clarete',
    'vacanti',
    'spulec',
    'adamn',
    'zmsmith',
    'nityaoberoi',
    'xie1989',
    'fabiomcosta',
    'suneel0101',
    'Bpless',
    'Mingweigu',
    'talsafran',
    'andrewgross',
    'rumela',
    'ajyang818',
    'lgroetzi',
    'mattRaoul',
    'hltbra',
    'farnja',
    'geraldoramos',
    'assisantunes',
    'ee99ee',
    'zkourouma',
]
GEO_IP_FILE_LOCATION = LOCAL_FILE('data', 'GeoIPCity.dat')

SSL_PRIVATE_KEY_FILE = LOCAL_FILE('')
