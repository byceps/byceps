#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run a worker for the job queue."""

import os
import sys

from redis import StrictRedis
from rq import Connection, Queue, Worker

from bootstrap.util import app_context


if __name__ == '__main__':
    config_name = os.environ.get('ENVIRONMENT')
    if config_name is None:
        sys.stderr.write("Environment variable 'ENVIRONMENT' must be set but isn't.")
        sys.exit()

    with app_context(config_name) as app:
        redis = StrictRedis(app.config['REDIS_URL'])
        with Connection(redis):
            queues = [Queue()]
            worker = Worker(queues)
            worker.work()
