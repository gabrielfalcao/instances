# -*- coding: utf-8 -*-

import os
import sys
import logging

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


__all__ = 'app',

class App(object):
    """Manage the main web app and all its subcomponents.

    By subcomponents I mean the database access, the command interface,
    the static assets, etc.
    """
    testing_mode = bool(os.getenv('INSTANCES_TESTING_MODE', False))

    def __init__(self, settings_path='instances.settings'):
        self.web = Flask(__name__)

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
