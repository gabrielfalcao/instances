#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import gevent
import json
from flask import (
    Blueprint, request, session, render_template, redirect, g, flash, Response, url_for
)
from instances import settings
from instances.api import GithubUser, GithubEndpoint, GithubRepository
from instances.handy.decorators import requires_login
from instances.handy.functions import user_is_authenticated

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

    github_user_data = GithubUser.fetch_info(token)

    github_user_data['github_token'] = token

    g.user = User.get_or_create_from_github_user(github_user_data)
    session['github_user_data'] = github_user_data

    return redirect(next_url)


@mod.context_processor
def inject_basics():
    return dict(
        settings=settings,
    )


@mod.route("/")
def index():
    if 'github_user_data' in session:
        return render_template('dashboard.html', github_user=session['github_user_data'])
    else:
        return render_template('index.html')


@mod.route("/account")
def show_settings():
    if 'github_user_data' in session:
        return render_template('account.html', github_user=session['github_user_data'])

    return redirect(url_for('.index'))



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
