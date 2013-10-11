#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import httpretty
from .base import user_test
from instances.testing import Client
from instances.models import Log


# @httpretty.activate
# @user_test
# def test_anonymous_index(context):
#     ("An anonymous user that goes to / should be redirected to the explore")

#     http = Client()

#     response = http.get("/")
#     (response
#      .should
#      .have
#      .property("location")
#      .being
#      .equal("http://localhost/explore"))


# @httpretty.activate
# @user_test
# def test_authenticated_index(context):
#     ("An authenticated user that goes to / should be redirected to his page")

#     http = Client()
#     with http.session_transaction() as session:
#         session['github_user_data'] = {
#             'login': 'octocat',
#         }

#     response = http.get("/")
#     (response
#      .should
#      .have
#      .property("location")
#      .being
#      .equal("http://localhost/octocat"))


# @httpretty.activate
# @user_test
# def test_logging(context):
#     ("An anonymous user that goes to / should be redirected to the explore")

#     http = Client()

#     payload = json.dumps({
#         'criteria': 'Attempt to search',
#         'bookmark_id': 123,
#         'project': 'foo/bar',
#     })
#     response = http.post("/search", data=payload, content_type="application/json")

#     logs = Log.all()

#     logs.should.have.length_of(1)

#     log = logs[0]

#     log.message.should.equal("[SEARCH] 123: Attempt to search")
#     log.data.should.equal(payload)

#     response.data.should.equal(json.dumps({"found": 0}))
