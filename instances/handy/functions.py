# -*- coding: utf-8 -*-

from flask import session


def user_is_authenticated():
    return bool(session.get('github_user_data', False))
