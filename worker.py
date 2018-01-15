#!/usr/bin/env python
"""Run a worker for the job queue.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from rq import Worker

from byceps.util.jobqueue import connection, get_queue
from byceps.util.system import get_config_filename_from_env_or_exit

from bootstrap.util import app_context


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()

    with app_context(config_filename):
        with connection():
            queues = [get_queue()]

            worker = Worker(queues)
            worker.work()
