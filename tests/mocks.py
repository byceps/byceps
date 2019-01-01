"""
tests.mocks
~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
"""

from unittest.mock import MagicMock

from redis import StrictRedis


def strict_redis_client_from_url(url):
    mock = MagicMock()
    mock.__class__ = StrictRedis
    return mock
