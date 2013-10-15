# -*- coding: utf-8 -*-
import math
import colorsys
from flask import session, g
from pygeoip import GeoIP as PyGEOIP
from pygeoip import GeoIPError
from instances import settings
from instances.log import logger

geoip = PyGEOIP(settings.GEO_IP_FILE_LOCATION)


def user_is_authenticated():
    from instances import settings
    from instances.models import User
    data = session.get('github_user_data', False)
    if data:
        g.user = User.get_or_create_from_github_user(data)

    return data and data['login'] in settings.BETA_USERS



def get_distance(loc_1, loc_2):
    return (1 * math.sqrt(math.pow((69.1 * (loc_1.latitude - loc_2.latitude)), 2) + math.pow((53 * (loc_1.longitude - loc_2.longitude)), 2)))


def geo_data_for_ip(ip_address):
    try:
        return geoip.record_by_addr(ip_address)
    except GeoIPError:
        logger.exception("Failed to get info for ip: %s", ip_address)
        return None
