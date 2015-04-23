# -*- coding: utf-8 -*-

"""
byceps.util.jobqueue
~~~~~~~~~~~~~~~~~~~~

An asynchronously processed job queue based on Redis_ and RQ_.


.. _Redis: http://redis.io/
.. _RQ:    http://python-rq.org/

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from contextlib import contextmanager

from rq import Connection, Queue

from byceps import redis


@contextmanager
def connection():
    with Connection(redis.get_connection()):
        yield


def get_queue():
    return Queue()


def enqueue(*args, **kwargs):
    """Add the function call to the queue as a job."""
    with connection():
        queue = get_queue()
        queue.enqueue(*args, **kwargs)
