#!/usr/bin/env python
"""Run a worker for the job queue.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from rq import Worker

from byceps.application import create_app
from byceps.util.jobqueue import connection, get_queue
from byceps.util.system import get_config_filename_from_env_or_exit


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()

    app = create_app(config_filename)

    with app.app_context():
        with connection():
            queues = [get_queue(app)]

            worker = Worker(queues)
            worker.work(with_scheduler=True)
