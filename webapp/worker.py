#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run a worker for the job queue."""

import os
import sys

from redis import StrictRedis
from rq import Connection, Queue, Worker

from byceps.application import create_app


if __name__ == '__main__':
    environment = os.environ.get('ENVIRONMENT')
    if environment is None:
        sys.stderr.write("Environment variable 'ENVIRONMENT' must be set but isn't.")
        sys.exit()

    app = create_app(environment, initialize=False)

    with app.app_context():
        redis = StrictRedis(app.config['REDIS_URL'])
        with Connection(redis):
            queues = [Queue()]
            worker = Worker(queues)
            worker.work()
