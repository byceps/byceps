# -*- coding: utf-8 -*-

"""
byceps.redis
~~~~~~~~~~~~

Redis_ integration.

.. _Redis: http://redis.io/

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import current_app
from redis import StrictRedis


def init_app(app):
    """Create a Redis connection object according to the configuration
    and attach it to the application.
    """
    url = app.config['REDIS_URL']
    app.extensions['redis'] = StrictRedis.from_url(url)


def get_connection():
    return current_app.extensions['redis']
