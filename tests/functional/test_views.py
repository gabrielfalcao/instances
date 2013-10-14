#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from redis import Redis
from mock import patch
from instances.testing import app
from sure import scenario
from flask import request, Request


def prepare_redis(context):
    context.redis = Redis()
    context.redis.flushall()


def prepare_app(context):
    class LocalTestClient(object):
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', '10.123.42.254')
            environ['HTTP_REFERRER'] = environ.get('HTTP_REFERRER', 'http://facebook.com')
            return self.app(environ, start_response)

    context.old_wsgi_app = app.web.wsgi_app
    app.web.wsgi_app = LocalTestClient(app.web.wsgi_app)
    context.client = lambda: app.web.test_client()


def cleanup_app(context):
    app.web.wsgi_app = context.old_wsgi_app


@scenario((prepare_redis, prepare_app), cleanup_app)
@patch('instances.views.time')
def test_base_request_recorder_view(context, time):
    ("A recording view should record the entire request data when requested")
    # Background: time.time is mocked to return "EPOCH_TIME"
    time.time.return_value = "EPOCH_TIME"

    # Given a http client
    http = context.client()

    # When I get the response for the project gabrielfalcao/HTTPretty
    response = http.get("/bin/gabrielfalcao/HTTPretty.svg")
    response.status_code.should.equal(200)

    # Then the redis key for that project should have 1 item
    context.redis.lrange("list:stats:github:gabrielfalcao/HTTPretty", 0, 1).should.equal([
        json.dumps({
            "request": {
                "headers": {
                    "Referrer": "http://facebook.com",
                    "Host": "localhost",
                    "Content-Type": "",
                    "Content-Length": "0"
                },
                "cookies": {},
                "remote_user": None,
                "user_agent": {
                    "platform": None,
                    "version": None,
                    "string": "",
                    "language": None,
                    "browser": None
                },
                "form": {},
                "remote_addr": "10.123.42.254",
                "query_string": "",
                "referrer": None,
                "args": {},
                "data": ""
            }, "time": 'EPOCH_TIME'})
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
    response.status_code.should.equal(302)
    response.headers.should.have.key('Location').being.equal('http://localhost/thank-you')

    # Then the redis key for that project should have 1 item
    list(context.redis.smembers("set:pitch-subscribers")).should.equal([
        json.dumps({'email': 'foo@bar.com', 'donor': False})])


@scenario((prepare_redis, prepare_app), cleanup_app)
def test_save_email_interested_private_beta(context):
    ("A post to /subscribe with an email and donor=true should "
     "record the person's email in a key for donors")
    # Given a http client
    http = context.client()

    # When I post en email to /subscribe
    response = http.post('/subscribe', data={
        'email': 'foo@bar.com',
        'beta-please': 'true',
    })
    response.status_code.should.equal(302)
    response.headers.should.have.key('Location').being.equal('http://localhost/thank-you')

    # Then the redis key for that project should have 1 item
    list(context.redis.smembers("set:pitch-private-beta-donors")).should.equal([
        json.dumps({'email': 'foo@bar.com', 'donor': True})])


@scenario((prepare_redis, prepare_app), cleanup_app)
def test_thank_you(context):
    ("A going to to /subscribe with an email should record the person's email")
    # Background: there are 3 people subscribed as donors
    context.redis.sadd("set:pitch-private-beta-donors", "email1")
    context.redis.sadd("set:pitch-private-beta-donors", "email2")
    context.redis.sadd("set:pitch-private-beta-donors", "email3")

    # Given a http client
    http = context.client()

    # And that the expected session keys are set
    with http.session_transaction() as session:
        session['subscription_email'] = 'foo@bar.com'
        session['subscription_is_donor'] = True

    # When I post en email to /thank-you
    response = http.get('/thank-you')

    # Then it should return 200
    response.status_code.should.equal(200)
    # And there should be 2 people in front of the last one in line
    response.data.should.contain('There are 2 people in the line')
