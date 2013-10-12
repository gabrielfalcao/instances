#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from redis import Redis
from instances.testing import app
from sure import scenario


def prepare_redis(context):
    context.redis = Redis()
    context.redis.flushall()


def prepare_app(context):
    class LocalTestClient(object):
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', '10.123.42.254')
            return self.app(environ, start_response)

    context.old_wsgi_app = app.web.wsgi_app
    app.web.wsgi_app = LocalTestClient(app.web.wsgi_app)
    context.client = lambda: app.web.test_client()


def cleanup_app(context):
    app.web.wsgi_app = context.old_wsgi_app



@scenario((prepare_redis, prepare_app), cleanup_app)
def test_base_request_recorder_view(context):
    ("A recording view should record the entire request data when requested")
    # Given a http client
    http = context.client()

    # When I get the response for the project gabrielfalcao/HTTPretty
    response = http.get("/bin/fork/gabrielfalcao/HTTPretty.gif")
    response.status_code.should.equal(200)

    # Then the redis key for that project should have 1 item
    context.redis.lrange("list:forks:github:gabrielfalcao/HTTPretty", 0, 1).should.equal([
        json.dumps({'request': {'remote_addr': '10.123.42.254'}})
    ])


@scenario((prepare_redis, prepare_app), cleanup_app)
def test_save_email_interested(context):
    ("A post to /subscribe with an email should record the person's email")
    # Given a http client
    http = context.client()

    # When I post en email to /subscribe
    response = http.post('/subscribe', data=dict(
        email='foo@bar.com',
    ))
    response.status_code.should.equal(200)

    # Then the redis key for that project should have 1 item
    list(context.redis.smembers("set:pitch-subscribers")).should.equal([
        json.dumps({'email': 'foo@bar.com', 'donator': False})])


@scenario((prepare_redis, prepare_app), cleanup_app)
def test_save_email_interested_private_beta(context):
    ("A post to /subscribe with an email and donator=true should "
     "record the person's email in a key for donators")
    # Given a http client
    http = context.client()

    # When I post en email to /subscribe
    response = http.post('/subscribe', data=dict(
        email='foo@bar.com',
        donator='true',
    ))
    response.status_code.should.equal(200)

    # Then the redis key for that project should have 1 item
    list(context.redis.smembers("set:pitch-private-beta-donators")).should.equal([
        json.dumps({'email': 'foo@bar.com', 'donator': True})])
