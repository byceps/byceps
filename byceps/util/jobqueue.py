"""
byceps.util.jobqueue
~~~~~~~~~~~~~~~~~~~~

An asynchronously processed job queue based on Redis_ and RQ_.

.. _Redis: https://redis.io/
.. _RQ:    https://python-rq.org/

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Callable
from datetime import datetime, UTC

from flask import current_app
from rq import Queue


def get_queue(app):
    is_async = app.config.get('JOBS_ASYNC', True)
    return Queue(connection=app.redis_client, is_async=is_async)


def enqueue(func: Callable, *args, **kwargs):
    """Add the function call to the queue as a job."""
    queue = get_queue(current_app)
    queue.enqueue(func, *args, **kwargs)


def enqueue_at(dt: datetime, func: Callable, *args, **kwargs):
    """Add the function call to the queue as a job to be executed at the
    specific time.
    """
    if dt.tzinfo is None:
        # Set UTC as timezine in naive datetime objects
        # to prevent rq from assuming local timezone.
        dt = dt.replace(tzinfo=UTC)

    queue = get_queue(current_app)
    queue.enqueue_at(dt, func, *args, **kwargs)
