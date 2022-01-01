"""
byceps.util.jobqueue
~~~~~~~~~~~~~~~~~~~~

An asynchronously processed job queue based on Redis_ and RQ_.

.. _Redis: https://redis.io/
.. _RQ:    https://python-rq.org/

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Callable

from flask import current_app
from rq import Connection, Queue


@contextmanager
def connection():
    with Connection(current_app.redis_client):
        yield


def get_queue(app):
    is_async = app.config['JOBS_ASYNC']
    return Queue(is_async=is_async)


def enqueue(func: Callable, *args, **kwargs):
    """Add the function call to the queue as a job."""
    with connection():
        queue = get_queue(current_app)
        queue.enqueue(func, *args, **kwargs)


def enqueue_at(dt: datetime, func: Callable, *args, **kwargs):
    """Add the function call to the queue as a job to be executed at the
    specific time.
    """
    if dt.tzinfo is None:
        # Set UTC as timezine in naive datetime objects
        # to prevent rq from assuming local timezone.
        dt = dt.replace(tzinfo=timezone.utc)

    with connection():
        queue = get_queue(current_app)
        queue.enqueue_at(dt, func, *args, **kwargs)
