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
    run("apt-get install -q=2 -y aptitude")
    run("aptitude install -q=2 -y python-pip")
    run("aptitude install -q=2 -y python-dev")
    run("aptitude install -q=2 -y libmysqlclient-dev")
    run("aptitude install -q=2 -y mysql-client")
    run("aptitude install -q=2 -y redis-server")
    run("pip install -q curdling")
    run("curd install virtualenvwrapper")
    run("pip install virtualenvwrapper")

@runs_once
def deploy():
    release_name = commands.getoutput("git rev-parse HEAD").splitlines()[0].strip()
    release_path = '/srv/{0}/'.format(release_name)
    run("test -e {0} || mkdir {0}".format(release_path))
    #put(SOURCECODE_PATH, release_path)
    put(LOCAL_FILE('.conf', 'supervisor.conf'), "/etc/supervisor/conf.d/instances.conf")
    run("test -e /srv/venv || virtualenv --no-site-packages --clear /srv/venv")
    put(LOCAL_FILE('.conf', 'sitecustomize.py'), "/srv/venv/lib/python2.7/sitecustomize.py")

    run("rm -rf /srv/instances")
    run("ln -s {0} /srv/instances".format(release_path))
    run("/srv/venv/bin/pip install -r /srv/instances/requirements.txt")
    run("service supervisor stop")
    run("(ps aux | egrep supervisord | grep -v grep | awk '{ print $2 }' | xargs kill -9 2>&1>/dev/null) 2>&1>/dev/null || printf '\033[1;32mSupervisor is down\033[0m'")
    run("service supervisor start")
