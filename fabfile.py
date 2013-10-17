# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import commands
from datetime import datetime
from os.path import dirname, abspath, join
from fabric.api import run, runs_once, put

LOCAL_FILE = lambda *path: join(abspath(dirname(__file__)), *path)

SOURCECODE_PATH = LOCAL_FILE('*')

@runs_once
def create():
    run("apt-get -q=2 update")
    dependencies = [
        'git-core',
        'python-pip',
        'supervisor',
        'python-dev',
        'libmysqlclient-dev',
        'mysql-client',
        'redis-server',
        'libxml2-dev',
        'libxslt1-dev',
        'libevent-dev',
        'libev-dev',
        'virtualenvwrapper',
    ]
    run("apt-get install -q=2 -y aptitude")
    run("aptitude install -q=2 -y {0}".format(" ".join(dependencies)))
    run("test -e /srv && rm -rf /srv/")
    run("mkdir -p /srv/")


@runs_once
def deploy():
    release_path = '/srv/instances'
    put(LOCAL_FILE('.conf', 'ssh', 'id_rsa*'), "~/.ssh/")
    run("chmod 600 ~/.ssh/id_rsa*")
    run("test -e {0} || git clone git@github.com:gabrielfalcao/instances.git {0}".format(release_path))
    run("cd /srv/instances && git fetch --prune")
    run("cd /srv/instances && git reset --hard origin/master")
    run("cd /srv/instances && git clean -df")
    run("cd /srv/instances && git pull")
    run("test -e /srv/venv || virtualenv --no-site-packages --clear /srv/venv")

    put(LOCAL_FILE('.conf', 'sitecustomize.py.template'), "/srv/venv/lib/python2.7/sitecustomize.py")

    run("/srv/venv/bin/pip install -q -r /srv/instances/requirements.txt")
    run("mkdir -p /srv/certificates")

    put(LOCAL_FILE('.conf', 'ssl.key.dec'), "/srv/certificates/ssl.key")
    put(LOCAL_FILE('.conf', 'ssl.crt'), "/srv/certificates/ssl.crt")

    run("chmod 400 /srv/certificates/*")

    put(LOCAL_FILE('.conf', 'supervisor.http.conf'), "/etc/supervisor/conf.d/instances-http.conf")
    put(LOCAL_FILE('.conf', 'supervisor.ssl.conf'), "/etc/supervisor/conf.d/instances-ssl.conf")

    run("service supervisor stop")
    run("(ps aux | egrep supervisord | grep -v grep | awk '{ print $2 }' | xargs kill -9 2>&1>/dev/null) 2>&1>/dev/null || printf '\033[1;32mSupervisor is down\033[0m'")
    run("(ps aux | egrep gunicorn | grep -v grep | awk '{ print $2 }' | xargs kill -9 2>&1>/dev/null) 2>&1>/dev/null || printf '\033[1;32mGunicorn is down\033[0m'")
    run("service supervisor start")
