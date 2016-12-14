#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Run a worker for the job queue.

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import sys

from rq import Worker

from byceps.util.jobqueue import connection, get_queue
from byceps.util.system import get_config_filename_from_env

from bootstrap.util import app_context


def get_config_filename():
    try:
        return get_config_filename_from_env()
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit()


if __name__ == '__main__':
    config_filename = get_config_filename()

    with app_context(config_filename):
        with connection():
            queues = [get_queue()]

            worker = Worker(queues)
            worker.work()
