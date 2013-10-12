# -*- coding: utf-8 -*-
import os
import sys
import re
import json
import sure
import httpretty
from lxml import html as lhtml
from lettuce import world, before, after
from instances.testing import Client
from instances import db
from instances.models import (
    metadata,
    User,
    HttpCache,
)
from tests.functional.base import setup_httpretty
from webdriverplus import WebDriver


HTTPRETY_METHODS = [
    httpretty.GET,
    httpretty.POST,
    httpretty.PUT,
    httpretty.DELETE,
]



@before.all
def enable_httpretty(*args):
    httpretty.enable()
    setup_httpretty()


@before.all
def export_models(*args):
    world.User = User
    world.HttpCache = HttpCache


@before.each_scenario
def prepare_db(scenario):
    metadata.drop_all(db.engine)
    metadata.create_all(db.engine)


@after.each_scenario
def cleanup_db(scenario):
    conn = db.engine.connect()
    conn.execute(User.table.delete())
    conn.execute(HttpCache.table.delete())


@world.absorb
def web_client(login=None):
    http = Client()

    if login:
        with http.session_transaction() as session:
            session['github_user_data'] = {
                'login': login,
            }

    return http


@world.absorb
def get_dom(html):
    return lhtml.fromstring(html)

sure
