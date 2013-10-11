# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import commands
from datetime import datetime
from os.path import dirname, abspath, join
from fabric.api import run, runs_once, put

LOCAL_FILE = lambda *path: join(abspath(dirname(__file__)), *path)

SOURCECODE_PATH = LOCAL_FILE('*')


@runs_once
def deploy():
    release_name = commands.getoutput("git rev-parse HEAD").splitlines()[0].strip()
    release_path = '/srv/{0}/'.format(release_name)
    run("test -e {0} || mkdir {0}".format(release_path))
    put(SOURCECODE_PATH, release_path)
    put(LOCAL_FILE('supervisor.conf'), "/etc/supervisor/conf.d/yciui.conf")
    run("test -e /srv/venv || virtualenv --no-site-packages /srv/venv")
    run("rm -rf /srv/yciui")
    run("ln -s {0} /srv/yciui".format(release_path))
    run("chmod +x /srv/yciui/bin/flaskd")
    run("/srv/venv/bin/pip install -r /srv/yciui/requirements.txt")
    run("service supervisor stop")
    run("(ps aux | egrep supervisord | grep -v grep | awk '{ print $2 }' | xargs kill -9 2>&1>/dev/null) 2>&1>/dev/null || printf '\033[1;32mSupervisor is down\033[0m'")
    run("service supervisor start")
