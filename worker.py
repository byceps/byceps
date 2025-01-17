#!/usr/bin/env python
"""Run a worker for the job queue.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from rq import Worker

from byceps.application import create_worker_app
from byceps.config.integration import (
    read_configuration_from_file_given_in_env_var,
)
from byceps.util.jobqueue import get_queue
from byceps.util.sentry import configure_sentry_from_env


if __name__ == '__main__':
    configure_sentry_from_env('worker')

    config_overrides = read_configuration_from_file_given_in_env_var()

    app = create_worker_app(config_overrides=config_overrides)

    with app.app_context():
        queues = [get_queue(app)]

        worker = Worker(queues)
        worker.work(with_scheduler=True)
