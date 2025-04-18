#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import io
import re
import time
import gevent
import json
from flask import (
    Blueprint,
    request,
    session,
    render_template,
    redirect,
    g,
    flash,
    Response,
    url_for,
)
from instances import settings
from instances.api import GithubUser, GithubEndpoint, GithubRepository
from instances.handy.decorators import requires_login
from instances.handy.functions import user_is_authenticated, geo_data_for_ip
from instances.models import User
from instances.log import logger
from instances.core import KeyRing
from instances import db
from redis import Redis

mod = Blueprint('views', __name__)

if not settings.TESTING:
    PNG_DATA = io.open(settings.LOCAL_FILE('static', 'img', 'stats.png'), 'rb').read()
else:
    PNG_DATA = 'a fake png'

def json_response(data, status=200):
    return Response(json.dumps(data), mimetype="text/json", status=int(status))


def error_json_response(message, status=200):
    return json_response({
        'success': False,
        'error': {
            'message': message
        }
    }, status=status)



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



def get_events_for_user(token, github_user_data):
    api = GithubEndpoint(user.github_token, public=True)
    response = api.retrieve("/events")
    redis = Redis()
    redis.lpush("events-{login}".format(**github_user_data), response)


@mod.context_processor
def inject_basics():
    return dict(
        settings=settings,
        messages=session.pop('messages', []),
        github_user=session.get('github_user_data', None),
        json=json,
        len=len,
        full_url_for=lambda *args, **kw: settings.absurl(url_for(*args, **kw)),
        ssl_full_url_for=lambda *args, **kw: settings.sslabsurl(url_for(*args, **kw)),
        static_url=lambda path: "{0}/{1}".format(settings.STATIC_BASE_URL.rstrip('/'), path.lstrip('/')),
    )


@mod.route("/")
def index():
    if 'github_user_data' in session:
        return redirect(url_for('.dashboard'))

    return render_template('light-base.html')



@mod.route("/logout")
def logout():
    session.pop('github_user_data', '')
    return redirect('/')

@mod.route("/account")
@requires_login
def show_settings():
    return render_template('account.html')


@mod.route("/dashboard")
@requires_login
def dashboard():
    return render_template('dashboard.html')


@mod.route("/email")
@requires_login
def email():
    return render_template('email/thankyou.html')


@mod.route("/bin/dashboard/modal/<project>.html")
@requires_login
def ajax_tracking_modal_html(project):
    username = session['github_user_data']['login']
    user = User.using(db.engine).find_one_by(username=username)
    if not user:
        return render_template('403.html', **locals())

    api = GithubEndpoint(user.github_token, public=True)

    repository_fetcher = GithubRepository(api)
    repository = repository_fetcher.get(username, project)

    return render_template('dashboard/tracking-modal.html', repository=repository, username=username)


@mod.route("/bin/dashboard/repo-list.json")
@requires_login
def ajax_dashboard_repo_list():
    username = session['github_user_data']['login']
    key = KeyRing.for_user_project_name_set(username)

    repositories = g.user.list_repositories()

    repositories_by_name = dict([(r['full_name'], r) for r in repositories])
    redis = Redis()
    tracked_names = redis.smembers(key)
    tracked_repositories = [repositories_by_name[name] for name in tracked_names]

    return json_response({
        'tracked_repositories': tracked_repositories,
        'repositories': repositories,
        'repositories_by_name': repositories_by_name,
    })



@mod.route("/thank-you")
def thank_you():
    if not ('subscription_email' in session and 'subscription_is_donor' in session):
        return redirect('/')

    email = session['subscription_email']
    is_potential_donor = session['subscription_is_donor']

    key = DONOR_SET_KEYS[is_potential_donor]
    redis = Redis()
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


def record_stats(username, project):
    norecord = 'norecord' in request.args
    if norecord:
        return

    user = User.using(db.engine).find_one_by(username=username)

    data = {
        'request': {
            'remote_addr': request.remote_addr,
            'remote_user': request.remote_user,
            'referrer': request.referrer,
            'headers': dict(request.headers),
            'args': dict(request.args),
            'form': dict(request.form),
            'data': request.data,
            'query_string': request.query_string,
            'cookies': dict(request.cookies or {}),
            'user_agent': {
                'browser': request.user_agent.browser,
                'platform': request.user_agent.platform,
                'language': request.user_agent.language,
                'string': request.user_agent.string,
                'version': request.user_agent.version,
            },
        },
        'geo': geo_data_for_ip(request.remote_addr),
        'time': time.time(),
    }
    key = KeyRing.for_user_project_stats_list(username, project)
    value = json.dumps(data)
    redis = Redis()
    redis.rpush(key, value)
    set_key = KeyRing.for_user_project_name_set(username)
    redis.sadd(set_key, "{0}/{1}".format(username, project))


@mod.route("/bin/<username>/<project>.svg")
def serve_stat_svg(username, project):
    record_stats(username, project)
    context = {
        'username': username,
        'project': project,
    }
    return Response(render_template('btn/stats.svg', **context), content_type='image/svg+xml')


@mod.route("/bin/<username>/<project>.png")
def serve_stat_png(username, project):
    record_stats(username, project)
    context = {
        'username': username,
        'project': project,
    }
    return Response(PNG_DATA, content_type='image/png')


@mod.route("/bin/btn/<kind>-<username>-<project>-<size>.html")
def serve_btn(kind, username, project, size):
    user = User.using(db.engine).find_one_by(username=username)
    size_meta = {
        'width': '52px',
        'height': '20px',
        'name': size,
    }
    if size == 'large':
        size_meta['width'] = '152px'
        size_meta['height'] = '30px'
    if not user or kind not in ['watchers', 'forks', 'follow']:
        return render_template('wrong-button.html', **{
            'username': username,
            'project': project,
            'size': size_meta,
        })

    api = GithubEndpoint(user.github_token, public=True)
    repository_fetcher = GithubRepository(api)

    repository = repository_fetcher.get(username, project)

    count = repository.get(kind, 0)

    TEXTS = {
        'watchers': 'Stars',
        'forks': 'Forks',
        'follow': 'Follow @{0}'.format(username),
    }

    HREFS = {
        'watchers': 'https://github.com/' + username + '/' + project + '/stargazers',
        'forks': 'https://github.com/' + username + '/' + project + '/network',
        'follow': 'https://github.com/' + username + '/followers',
    }
    context = {
        'kind': kind,
        'username': username,
        'repository': repository,
        'count': count,
        'size': size_meta,
        'text': TEXTS[kind],
        'href': HREFS[kind],
    }
    return render_template('btn/iframe.html', **context)


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
    return mod.github.authorize('user,user:email,user:follow')


def get_github_token(token=None):
    return session.get('github_token', token)  # might bug


def github_callback(token):
    from instances.models import User
    next_url = request.args.get('next') or '/'
    if not token:
        logger.error(u'You denied the request to sign in.')
        return redirect(next_url)

    session['github_token'] = token

    github_user_data = GithubUser.fetch_info(token, skip_cache=True)

    github_user_data['github_token'] = token

    g.user = User.get_or_create_from_github_user(github_user_data)
    session['github_user_data'] = github_user_data
    return redirect(next_url)
