#!/usr/bin/env python
"""Run a worker for the job queue.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from rq import Worker

from byceps.application import create_app
from byceps.util.jobqueue import connection, get_queue


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        with connection():
            queues = [get_queue(app)]

            worker = Worker(queues)
            worker.work(with_scheduler=True)
