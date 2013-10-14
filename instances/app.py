# -*- coding: utf-8 -*-

import os
import sys
import logging
import pickle

from datetime import timedelta
from uuid import uuid4
from redis import StrictRedis
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin

from flask import Flask, render_template
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy

from logging import getLogger, StreamHandler
from sqlalchemy import (
    create_engine,
    MetaData,
)

from instances.assets import AssetsManager
from instances.commands import init_command_manager
from instances import views




class RedisSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis=None, prefix='session:'):
        if redis is None:
            redis = StrictRedis(db=2)

        self.redis = redis
        self.prefix = prefix

    def generate_sid(self):
        return str(uuid4())

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.redis.delete(self.prefix + session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid, int(redis_exp.total_seconds()), val)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True,
                            domain=domain)


class App(object):
    """Manage the main web app and all its subcomponents.

    By subcomponents I mean the database access, the command interface,
    the static assets, etc.
    """
    testing_mode = bool(os.getenv('INSTANCES_TESTING_MODE', False))

    def __init__(self, settings_path='instances.settings'):
        self.web = Flask(__name__)

        # Preparing session
        self.web.session_interface = RedisSessionInterface()
        # Loading our settings
        self.web.config.from_object(settings_path)

        # Loading our JS/CSS
        self.assets = AssetsManager(self.web)
        self.assets.create_bundles()

        # Setting up our commands
        self.commands = init_command_manager(Manager(self.web))
        self.assets.create_assets_command(self.commands)

        # Setting up our database component
        self.db = SQLAlchemy(self.web)
        metadata = MetaData()

        # Time to register our blueprints
        views.mod.app = self
        views.mod.db = self.db
        views.mod.engine = self.db.engine
        self.web.register_blueprint(views.mod)

        if not self.testing_mode:
            self.setup_logging(output=sys.stderr, level=logging.ERROR)

        @self.web.errorhandler(500)
        def internal_error(exception):
            self.web.logger.exception(exception)
            return render_template('500.html'), 500

    def setup_logging(self, output, level):
        for logger in [self.web.logger, getLogger('sqlalchemy'), getLogger('instances.views')]:
            logger.addHandler(StreamHandler(output))
            logger.setLevel(level)

    @classmethod
    def from_env(cls):
        """Return an instance of `App` fed with settings from the env.
        """
        smodule = os.environ.get(
            'INSTANCES_SETTINGS_MODULE',
            'instances.settings'
        )
        return cls(smodule)


app = App.from_env()
