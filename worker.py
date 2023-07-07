#!/usr/bin/env python
"""Run a worker for the job queue.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from rq import Worker

from byceps.application import create_worker_app
from byceps.util.jobqueue import connection, get_queue
from byceps.util.sentry import configure_sentry_from_env


if __name__ == '__main__':
    configure_sentry_from_env()

    app = create_worker_app()

    with app.app_context():
        with connection():
            queues = [get_queue(app)]

            worker = Worker(queues)
            worker.work(with_scheduler=True)
