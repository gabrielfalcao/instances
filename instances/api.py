#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import ejson
import logging
import requests
from datetime import datetime


class GithubEndpoint(object):
    base_url = u'https://api.github.com'

    def __init__(self, token, cache=None, public=False):
        from instances.models import HttpCache
        self.history = []
        self.token = token
        self.cache = cache or HttpCache

        self.public = public
        self.headers = {
            'authorization': 'token {0}'.format(token),
            'X-GitHub-Media-Type: github.beta': 'github.beta',
            'User-Agent': 'instances/retriever',
        }
        self.log = logging.getLogger('instances.api')

    @property
    def last_response(self):
        return self.history and self.history[-1]

    def full_url(self, path):
        url = u"/".join([self.base_url, path.lstrip('/')])
        return url

    def find_cache_object(self, url):
        self.log.info("GET from CACHE %s at %s", url, str(time.time()))

        if self.public:
            return self.cache.find_one_by(url=url)
        else:
            return self.cache.find_one_by(url=url, token=self.token)

    def get_or_create_cache_object(self, url, content):
        kw = dict(url=url, content=content)

        if not self.public:
            kw['token'] = self.token

        existing = self.cache.find_one_by(url=kw['url'])
        return existing or self.cache.create(**kw)

    def get_from_cache(self, path, headers, data=None):
        url = self.full_url(path)

        cached = self.find_cache_object(url)

        if not cached:
            return {}

        now = datetime.now()
        elapsed = now - cached.updated_at

        if elapsed.total_seconds() > self.cache.TIMEOUT:
            return {}

        d = cached.to_cache_dict()
        try:
            ejson.loads(d['response_data'])
        except ValueError:
            self.log.exception('Truncated cache data')
            return {}

        return d

    def get_from_web(self, path, headers, data=None):
        url = self.full_url(path)
        data = data or {}

        request = {
            'url': url,
            'data': data,
            'headers': headers,
        }
        response = {}
        error = None
        try:
            self.log.info("GET from WEB %s at %s", url, str(time.time()))
            response = requests.get(**request)
        except Exception as e:
            error = e
            self.log.exception("Failed to retrieve `%s` with data %s", path, repr(data))

        return {
            'url': url,
            'request_headers': headers,
            'request_data': data,
            'response_headers': dict(response.headers),
            'error': error,
            'response_data': response.content,
            'cached': False,
            'status_code': response.status_code,
        }

    def retrieve(self, path, data=None):
        headers = self.headers
        response = self.get_from_cache(path, headers, data)
        if not response:
            response = self.get_from_web(path, headers, data)
            response_data = response['response_data'].decode('utf-8')
            cached = self.get_or_create_cache_object(response['url'], response_data)
            cached.content = response_data
            cached.headers = ejson.dumps(response['response_headers'])
            cached.status_code = response['status_code']
            cached.save()

        self.history.append(response)
        return self.json(response)

    def save(self, path, data=None):
        return self.json(requests.put(
            self.full_url(path),
            headers=self.headers,
        ))

    def json(self, response):
        return ejson.loads(response['response_data'])


class Resource(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    @classmethod
    def from_token(cls, token):
        endpoint = GithubEndpoint(token)
        return cls(endpoint)


class GithubUser(Resource):
    @classmethod
    def fetch_info(cls, token):
        instance = cls.from_token(token)
        return instance.endpoint.retrieve('/user')

    def get_starred(self, username):
        return self.endpoint.retrieve('/users/{0}/starred'.format(username))


class GithubRepository(Resource):
    def request_markdown(self, owner, project, request_path):
        url_prefix = "https://raw.github.com/{0}/{1}/master/".format(owner, project)
        reply = self.endpoint.retrieve(request_path)
        raw = reply['content'].decode(reply['encoding'])
        if reply['encoding'] != 'utf-8':
            raw = raw.decode('utf-8')

        filename = reply['name']

        if filename.lower().endswith('.md') or filename.lower().endswith('.markdown'):
            document = Markment(raw, url_prefix=url_prefix)
            return document.rendered, document.index()
        else:
            return raw, []

    def retrieve_docs(self, owner, project, path):
        path = path.lstrip("/")
        request_path = '/repos/{0}/{1}/contents/{2}'.format(owner, project, path)
        return self.request_markdown(owner, project, request_path)

    def get_readme(self, owner, project):
        request_path = '/repos/{0}/{1}/readme'.format(owner, project)
        return self.request_markdown(owner, project, request_path)

    def get_languages(self, owner, project):
        return self.endpoint.retrieve(
            '/repos/{0}/{1}/languages'.format(owner, project))

    def get_owner(self, owner):
        response = self.endpoint.retrieve(
            '/users/{0}'.format(owner))

        return response

    def get(self, owner, project):
        return self.endpoint.retrieve('/repos/{0}/{1}'.format(owner, project))
