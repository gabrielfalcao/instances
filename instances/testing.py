# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from instances.app import app

Client = lambda: app.web.test_client()
