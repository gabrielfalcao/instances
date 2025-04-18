#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
import json
import logging
import requests
from datetime import datetime
from redis import StrictRedis


class GithubEndpoint(object):
    base_url = u'https://api.github.com'
    TIMEOUT = 60 * 10  # 10 minutes
    def __init__(self, token, public=False):
        self.token = token
        self.redis = StrictRedis(db=1)

        self.public = public
        self.headers = {
            'authorization': 'token {0}'.format(token),
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
        }
        self.log = logging.getLogger('instances.api')

    def full_url(self, path):
        url = u"/".join([self.base_url, path.lstrip('/')])
        return url

    def find_cache_object(self, url):
        key = self.key(url)
        data = self.redis.get(key)
        if data:
            self.log.info("GET from CACHE %s at %s", url, str(time.time()))
            return json.loads(data)

    def key(self, url):
        if self.public:
            key = "cache:url:{0}".format(url)
        else:
            key = "cache:token:{1}:url:{0}".format(self.token, url)

        return key

    def create_cache_object(self, response):
        key = self.key(response['url'])
        content = json.dumps(response)
        self.redis.setex(key, self.TIMEOUT, content)

    def get_from_cache(self, path, headers, data=None):
        url = self.full_url(path)
        return self.find_cache_object(url) or {}

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

        primitive_response = {
                'url': url,
                'request_headers': headers,
                'request_data': data,
                'response_headers': dict(response.headers),
                'error': error,
                'response_data': response.content,
                'cached': False,
                'status_code': response.status_code,
            }
        if str(response.status_code).startswith("2"):
            return primitive_response

        self.log.warning("Failed to retrieve `%s` with data %s", path, json.dumps(primitive_response, indent=2))

    def retrieve(self, path, data=None, skip_cache=False):
        headers = self.headers
        if skip_cache:
            response = None
        else:
            response = self.get_from_cache(path, headers, data)

        if not response:
            response = self.get_from_web(path, headers, data)
            if response:
                self.create_cache_object(response)

        return response

    def save(self, path, data=None):
        return self.json(requests.put(
            self.full_url(path),
            headers=self.headers,
        ))


class Resource(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    @classmethod
    def from_token(cls, token):
        endpoint = GithubEndpoint(token)
        return cls(endpoint)


class GithubUser(Resource):
    @classmethod
    def fetch_info(cls, token, skip_cache=False):
        instance = cls.from_token(token)
        response = instance.endpoint.retrieve('/user', skip_cache=skip_cache)
        if not response:
            return {}
        return json.loads(response['response_data'])

    def get_starred(self, username):
        path = '/users/{0}/starred'.format(username)
        response = self.endpoint.retrieve(path)
        return json.loads(response['response_data'])

    def get_next_path(self, response):
        raw = response['response_headers'].get('link')
        # https://api.github.com/user/54914/repos?sort=pushed&page=2>; rel="next",
        if raw:
            found = re.search(r'https://api.github.com([^;]+); rel="next"', raw)
            if found:
                return found.group(1)

    def get_path_recursively(self, path):
        response = self.endpoint.retrieve(path)
        value = json.loads(response['response_data'])
        next_path = self.get_next_path(response)
        if next_path:
            value += self.get_path_recursively(next_path)

        return value

    def get_repositories(self, username):
        path = '/users/{0}/repos?sort=pushed'.format(username)
        return self.get_path_recursively(path)


class GithubRepository(Resource):
    def get(self, owner, project):
        path = '/repos/{0}/{1}'.format(owner, project)
        response = self.endpoint.retrieve(path)
        return json.loads(response['response_data'])
