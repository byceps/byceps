#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run a worker for the job queue."""

import sys

from redis import StrictRedis
from rq import Connection, Queue, Worker

from bootstrap.util import app_context, get_config_name_from_env


if __name__ == '__main__':
    try:
        config_name = get_config_name_from_env()
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit()

    with app_context(config_name) as app:
        redis = StrictRedis(app.config['REDIS_URL'])
        with Connection(redis):
            queues = [Queue()]
            worker = Worker(queues)
            worker.work()
