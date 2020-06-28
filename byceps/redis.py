"""
byceps.redis
~~~~~~~~~~~~

Redis_ integration.

.. _Redis: https://redis.io/

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import _app_ctx_stack as stack
from redis import StrictRedis


EXTENSION_KEY = 'byceps_redis'

CONTEXT_ATTRIBUTE_NAME = 'redis_client'


class Redis:

    def init_app(self, app):
        url = app.config['REDIS_URL']
        self._client = StrictRedis.from_url(url)

        app.extensions[EXTENSION_KEY] = self

    @property
    def client(self):
        ctx = stack.top

        if ctx is not None:
            if not hasattr(ctx, CONTEXT_ATTRIBUTE_NAME):
                setattr(ctx, CONTEXT_ATTRIBUTE_NAME, self._client)

            return getattr(ctx, CONTEXT_ATTRIBUTE_NAME)


redis = Redis()
