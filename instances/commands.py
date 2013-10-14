#!/usr/bin/env python
# -*- coding: utf-8; -*-
import os
import time
import json

from datetime import datetime

from flask.ext.script import Command
from flask.ext.script import Command, Option


LOGO = """

\033[1;37m        .--.                \033[1;33m.88b  d88.  .d8b.     d88b  .d88b.  d8888b.
\033[1;37m       /    \               \033[1;33m88'YbdP`88 d8' `8b    `8P' .8P  Y8. 88  `8D
\033[1;37m      ## a  a       _       \033[1;33m88  88  88 88ooo88     88  88    88 88oobY'
\033[1;37m      (   '._)     |_|      \033[1;33m88  88  88 88~~~88     88  88    88 88`8b
\033[1;37m       |'-- |      | |      \033[1;33m88  88  88 88   88 db. 88  `8b  d8' 88 `88.
\033[1;37m     _.\___/_   ___|_|___   \033[1;33mYP  YP  YP YP   YP Y8888P   `Y88P'  88   YD
\033[1;37m   .'\> \Y/|<'.  '._.-'     \033[1;33m
\033[1;37m  /  \ \_\/ /  '-' /        \033[1;33md8888b.  .d88b.  .88b  d88.  .d88b.
\033[1;37m  | --'\_/|/ |   _/         \033[1;33m88  `8D .8P  Y8. 88'YbdP`88 .8P  Y8.
\033[1;37m  |___.-' |  |`'`           \033[1;33m88   88 88    88 88  88  88 88    88
\033[1;37m    |     |  |              \033[1;33m88   88 88    88 88  88  88 88    88
\033[1;37m    |    / './              \033[1;33m88  .8D `8b  d8' 88  88  88 `8b  d8'
\033[1;37m   /__./` | |               \033[1;33mY8888D'  `Y88P'  YP  YP  YP  `Y88P'
\033[1;37m      \   | |
\033[1;37m       \  | |
\033[1;37m       ;  | |
\033[1;37m       /  | |
\033[1;37m      |___\_.\_
\033[1;37m      `-'--'---'
\033[0m\r"""


class Runserver(Command):
    def run(self):
        from instances.server import app
        print "\033[1;37mServing Instances on {0}:{1}\033[0m".format(settings.HOST, settings.PORT)
        server.serve_forever()


class Check(Command):
    def run(self):
        from instances.app import App
        from instances.settings import absurl
        from traceback import format_exc
        app = App.from_env()
        HEALTHCHECK_PATH = "/"
        try:
            print LOGO
            print "SMOKE TESTING APPLICATION"
            app.web.test_client().get(HEALTHCHECK_PATH)
        except Exception as e:
            print "OOPS"
            print "An Exception happened when making a smoke test to \033[1;37m'{0}'\033[0m".format(absurl(HEALTHCHECK_PATH))
            print format_exc(e)
            raise SystemExit(3)

def init_command_manager(manager):
    manager.add_command('run', Runserver())
    manager.add_command('check', Check())
    return manager
