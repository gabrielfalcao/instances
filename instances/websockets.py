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


class Namespace(BaseNamespace):
    def __init__(self, *args, **kw):
        super(Namespace, self).__init__(*args, **kw)
        self.app = Semaphore()
        self.app.acquire()

    def on_stop(self, msg):
        self.app.release()

    def should_live(self):
        return self.app.locked()

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
        overall_key = "set:github:{username}/{project}".format(**data)
        raw_overall = map(json.loads, redis.smembers(overall_key))
        overall = sorted(raw_overall, key=lambda x: x['time'], reverse=True)
        by_category = {
            'overall': overall,
        }
        for kind in ['watchers', 'forks', 'follow']:
            key = "list:{0}:github:{username}/{project}".format(kind, **data)
            raw_visitors = redis.lrange(key, 0, 1000)
            visitors = map(json.loads, raw_visitors)
            by_category[kind] = visitors

        stats = {}
        for cat, visitors in by_category.iteritems():
            stats[cat] = len(visitors)

        value = {
            'by_category': by_category,
            'stats': stats,
        }
        print stats
        return value

    def random_status(self, data):
        if not isinstance(data, dict) or data.keys() != ["username", "project"]:
            return

        redis = Redis()
        while self.should_live():
            visitors = self.get_visitors(redis, data)
            self.emit("visitors", visitors)
            gevent.sleep(.3)

    def on_repository_statistics(self, msg):
        workers = [
            self.spawn(self.random_status, msg),
        ]
        gevent.joinall(workers)


NAMESPACES = {"": StatsSender}
