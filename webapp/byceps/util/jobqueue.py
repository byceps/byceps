# -*- coding: utf-8 -*-

"""
byceps.util.jobqueue
~~~~~~~~~~~~~~~~~~~~

An asynchronously processed job queue based on Redis_ and RQ_.


.. _Redis: http://redis.io/
.. _RQ:    http://python-rq.org/

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import current_app
from redis import StrictRedis


def get_redis_connection():
    """Return a Redis connection, based on the app's configuration."""
    url = current_app.config['REDIS_URL']
    return StrictRedis(url)
