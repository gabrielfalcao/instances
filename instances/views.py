#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import time
import gevent
import json
from flask import (
    Blueprint, request, session, render_template, redirect, g, flash, Response, url_for
)
from instances import settings
from instances.api import GithubUser, GithubEndpoint, GithubRepository
from instances.handy.decorators import requires_login
from instances.handy.functions import user_is_authenticated
from instances.models import User
from instances import db
from redis import Redis
from flaskext.github import GithubAuth

mod = Blueprint('views', __name__)


def json_response(data, status=200):
    return Response(json.dumps(data), mimetype="text/json", status=int(status))


def error_json_response(message):
    return json_response({'success': False, 'error': {'message': message}})


github = GithubAuth(
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    session_key='user_id',
    # request_token_params={'scope': 'user,user:email,user:follow,repo,repo:status'}
)

@mod.before_request
def prepare():
    g.user = None

def add_message(message, error=None):
    if 'messages' not in session:
        session['messages'] = []

    session['messages'].append({
        'text': message,
        'time': time.time(),
        'alert_class': error is None and 'uk-alert-success' or 'uk-alert-danger',
        'error': error,
    })

@github.access_token_getter
def get_github_token(token=None):
    return session.get('github_token', token)  # might bug


@mod.route('/.sys/callback')
@github.authorized_handler
def github_callback(resp):
    from instances.models import User
    next_url = request.args.get('next') or '/'
    if resp is None:
        print (u'You denied the request to sign in.')
        return redirect(next_url)

    error = resp.get('error')

    if error:
        flash(error)
        return json.dumps(error)

    token = resp['access_token']
    session['github_token'] = token

    github_user_data = GithubUser.fetch_info(token, skip_cache=True)

    github_user_data['github_token'] = token

    g.user = User.get_or_create_from_github_user(github_user_data)
    session['github_user_data'] = github_user_data

    return redirect(next_url)


@mod.context_processor
def inject_basics():
    return dict(
        settings=settings,
        messages=session.pop('messages', []),
        github_user=session.get('github_user_data', None),
        json=json,
        full_url_for=lambda *args, **kw: settings.absurl(url_for(*args, **kw))
    )


@mod.route("/")
def index():
    if 'github_user_data' in session:
        return redirect(url_for('.dashboard'))

    return render_template('index.html')


@mod.route("/account")
@requires_login
def show_settings():
    return render_template('account.html')


@mod.route("/dashboard")
@requires_login
def dashboard():
    redis = Redis()
    key = "set:{login}:repositories".format(**session['github_user_data'])

    repositories = g.user.list_repositories()
    tracked_repositories = map(json.loads, redis.smembers(key))

    def repository_is_being_tracked(repo):
        for possible in tracked_repositories:
            if repo['full_name'] == possible['full_name']:
                return True

        return False

    context = {
        'tracked_repositories': tracked_repositories,
        'repositories': repositories,
        'repository_is_being_tracked': repository_is_being_tracked
    }
    return render_template('dashboard.html', **context)

@mod.route("/thank-you")
def thank_you():
    if not ('subscription_email' in session and 'subscription_is_donor' in session):
        return redirect('/')

    redis = Redis()

    email = session['subscription_email']
    is_potential_donor = session['subscription_is_donor']

    key = DONOR_SET_KEYS[is_potential_donor]
    total_subscribers = redis.scard(key)

    context = {
        'subscription_email': email,
        'total_subscribers': total_subscribers
    }
    return render_template('thank_you.html', **context)

DONOR_SET_KEYS = {
    False: "set:pitch-subscribers",
    True: "set:pitch-private-beta-donors"
}

@mod.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get('email')

    if not email:
        add_message("Please provide your email", error="Missing Info")
        return redirect(url_for('.index'))

    is_potential_donor = request.form.get('beta-please') == 'true'
    data = {'email': email, 'donor': is_potential_donor}

    key = DONOR_SET_KEYS[is_potential_donor]
    value = json.dumps(data)

    redis = Redis()
    redis.sadd(key, value)

    session['subscription_email'] = email
    session['subscription_is_donor'] = is_potential_donor
    return redirect(url_for(".thank_you"))


@mod.route("/robots.txt")
def robots_txt():
    Disallow = lambda string: 'Disallow: {0}'.format(string)
    return Response("User-agent: *\n{0}\n".format("\n".join([
        Disallow('/bin/*'),
        Disallow('/thank-you'),
    ])))


@mod.route("/bin/btn/<kind>-<username>-<project>-<size>.html")
def serve_btn(kind, username, project, size):
    user = User.using(db.engine).find_one_by(username=username)
    if not user or kind not in ['watchers', 'forks', 'follow']:
        return render_template('wrong-button.html', **locals())

    api = GithubEndpoint(user.github_token, public=True)
    repository_fetcher = GithubRepository(api)

    repository = repository_fetcher.get(username, project)

    data = {
        'request': {
            'remote_addr': request.remote_addr,
            'remote_user': request.remote_user,
            'referrer': request.referrer,
            'headers': dict(request.headers),
            'form': dict(request.form),
            'data': request.data,
            'query_string': request.query_string,
        }
    }
    key = "list:{2}:github:{0}/{1}".format(username, project, kind)
    value = json.dumps(data)

    count = repository.get(kind, 0)

    redis = Redis()
    redis.rpush(key, value)

    key = "set:{0}:repositories".format(username)
    redis.sadd(key, json.dumps(repository))

    context = {
        'kind': kind,
        'username': username,
        'repository': repository,
        'count': count,
        'size': size,
    }
    return render_template('github-btn.html', **context)


@mod.route("/bin/json/<username>")
def json_world_map_for_user(username):
    path = settings.LOCAL_FILE('world-population.geo.json')
    with open(path) as fd:
        return Response(fd.read(), content_type="text/json")


@mod.route("/500")
def five00():
    return render_template('500.html')


@mod.route("/.healthcheck")
def healthcheck():
    return render_template('healthcheck.html')


@mod.route("/.ok")
def ok():
    return Response('YES\n\r')


@mod.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@mod.route('/login')
def login():
    cb = settings.absurl('.sys/callback')
    return github.authorize(callback_url=cb)
