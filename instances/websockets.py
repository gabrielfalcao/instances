#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gevent
import random
import traceback
import json
from itertools import chain
from gevent.coros import Semaphore
from datetime import datetime
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from redis import Redis
from instances.core import KeyRing
from instances.models import User
from instances import db
from instances.api import GithubUser, GithubEndpoint, GithubRepository
from instances.data.aggregators import VisitorAggregator

redis = Redis()

class Namespace(BaseNamespace):
    def humanized_now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def serialize(self, data):
        return json.dumps(data)

    def format_exception(self, exc):
        if exc:
            return traceback.format_exc(exc)

        return ''

class InstancesBroadcaster(Namespace, BroadcastMixin):
    def broadcast_status(self, text, error=None):
        traceback = self.format_exception(error)
        css_class = error and 'error' or 'success'

        payload = self.serialize({
            'text': text,
            'traceback': traceback,
            'ok': not error,
            'when': self.humanized_now(),
            'class': css_class
        })
        self.broadcast_event('status', payload)
        if error:
            gevent.sleep(30)


class StatsSender(InstancesBroadcaster):
    def get_visitors(self, redis, data):
        username = data['username']
        project = data['project']

        user = User.using(db.engine).find_one_by(username=username)
        if not user:
            self.stop()
            return

        api = GithubEndpoint(user.github_token, public=True)
        repository_fetcher = GithubRepository(api)

        repository = repository_fetcher.get(username, project)

        key = KeyRing.for_user_project_stats_list(username, project)
        raw_visitors = redis.lrange(key, 0, 1000)
        visitors = map(json.loads, raw_visitors)
        aggregate_visitors = VisitorAggregator(visitors)

        value = {
            'visitors': visitors,
            'by_country': aggregate_visitors.by_country(),
            'total': len(visitors),
            'repository': repository,
            'original_payload': data,
        }
        return value

    def random_status(self, data):
        if not isinstance(data, dict) or data.keys() != ["username", "project"]:
            return

        visitors = self.get_visitors(redis, data)
        key = "visitors"
        self.emit(key, visitors)

    def on_repository_statistics(self, msg):
        workers = [
            self.spawn(self.random_status, msg),
        ]
        gevent.joinall(workers)


NAMESPACES = {"": StatsSender}
