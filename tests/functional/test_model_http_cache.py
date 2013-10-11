#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import db_test
from freezegun import freeze_time
from httpretty import HTTPretty, httprettified

from instances.api import GithubEndpoint
from instances.models import HttpCache


@db_test
@httprettified
@freeze_time("2013-04-14 00:00:00")
def test_get_from_cache(context):
    ("Retrieving a url with cache")
    HTTPretty.register_uri(HTTPretty.GET, "https://api.github.com/user",
                           body='{"login": "gabrielfalcao"}',
                           content_type="application/json")

    api = GithubEndpoint('SOMETOKEN')
    data = api.retrieve("/user")
    data.should.have.key("login").being.equal("gabrielfalcao")

    cached = HttpCache.find_one_by(url="https://api.github.com/user")
    cached.should_not.be.none
    cached.content.should.equal('{"login": "gabrielfalcao"}')
    cached.headers.should.equal(
        '{'
        '"status": "200", "content-length": "26", '
        '"date": "Sun, 14 Apr 2013 00:00:00 GMT", '
        '"content-type": "application/json", '
        '"connection": "close", "server": "Python/HTTPretty"}'
    )

    cached.id.should.equal(1)
    cached.token.should.equal('SOMETOKEN')

    cached.url.should.equal('https://api.github.com/user')
    cached.status_code.should.equal(200)
    cached.updated_at.year.should.equal(2013)
    cached.updated_at.month.should.equal(4)
    cached.updated_at.day.should.equal(14)


@db_test
@httprettified
def test_get_from_cache_twice(context):
    ("Retrieving a url with cache twice should return the same one")
    HTTPretty.register_uri(HTTPretty.GET, "https://api.github.com/user",
                           body='{"login": "gabrielfalcao"}',
                           content_type="application/json")

    api = GithubEndpoint('SOMETOKEN')
    with freeze_time("2013-04-14 00:00:00"):
        first = api.retrieve("/user")

    with freeze_time("2013-04-14 03:00:00"):
        last = api.retrieve("/user")

    first.should.equal(last)


@db_test
@httprettified
def test_get_from_cache_twice_after_timeout(context):
    ("Retrieving a url with cache twice after the timeout should retrieve again and cache again")
    HTTPretty.register_uri(
        HTTPretty.GET,
        "https://api.github.com/user",
        responses=[
            HTTPretty.Response(body='{"version": "1"}', status=201),
            HTTPretty.Response(body='{"version": "2"}', status=202),
        ]
    )

    api = GithubEndpoint('SOMETOKEN')
    with freeze_time("2013-04-14 00:00:00"):
        first = api.retrieve("/user")

    with freeze_time("2013-04-14 03:00:01"):
        last = api.retrieve("/user")

    first.should_not.equal(last)

    HttpCache.all().should.have.length_of(1)


@db_test
@httprettified
@freeze_time("2013-04-14 00:00:00")
def test_get_from_cache_twice_different_tokens(context):
    ("Retrieving a url with cache twice but with different tokens should result in different results")
    HTTPretty.register_uri(
        HTTPretty.GET,
        "https://api.github.com/user",
        responses=[
            HTTPretty.Response(body='{"version": "1"}', status=201),
            HTTPretty.Response(body='{"version": "2"}', status=202),
        ]
    )

    api1 = GithubEndpoint('SOMETOKEN')
    api2 = GithubEndpoint('GANESH')

    first = api1.retrieve("/user")
    last = api2.retrieve("/user")

    first.should_not.equal(last)


@db_test
@httprettified
@freeze_time("2013-04-14 00:00:00")
def test_get_from_cache_twice_different_tokens_but_public(context):
    ("Retrieving a url with cache twice, with different tokens but public should get from cache")
    HTTPretty.register_uri(
        HTTPretty.GET,
        "https://api.github.com/user",
        responses=[
            HTTPretty.Response(body='{"version": "1"}', status=201),
            HTTPretty.Response(body='{"version": "2"}', status=202),
        ]
    )

    api1 = GithubEndpoint('SOMETOKEN', public=True)
    api2 = GithubEndpoint('GANESH', public=True)

    first = api1.retrieve("/user")
    last = api2.retrieve("/user")

    first.should.equal(last)
