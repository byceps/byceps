"""
byceps.util.jobqueue
~~~~~~~~~~~~~~~~~~~~

An asynchronously processed job queue based on Redis_ and RQ_.

.. _Redis: https://redis.io/
.. _RQ:    https://python-rq.org/

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from contextlib import contextmanager
from typing import Callable

from flask import current_app
from rq import Connection, Queue

from byceps.redis import redis


@contextmanager
def connection():
    with Connection(redis.client):
        yield


def get_queue(app):
    is_async = app.config['JOBS_ASYNC']
    return Queue(is_async=is_async)


def enqueue(func: Callable, *args, **kwargs):
    """Add the function call to the queue as a job."""
    with connection():
        queue = get_queue(current_app)
        queue.enqueue(func, *args, **kwargs)
