# -*- coding: utf-8 -*-

from flask import session, g

def user_is_authenticated():
    from instances import settings
    from instances.models import User
    data = session.get('github_user_data', False)
    if data:
        g.user = User.get_or_create_from_github_user(data)

    return data and data['login'] in settings.BETA_USERS
