"""
byceps.cli.command.worker
~~~~~~~~~~~~~~~~~~~~~~~~~

Start a worker to process the queue.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click
from rq import Worker

from byceps.application import create_worker_app
from byceps.config.converter import convert_config
from byceps.config.integration import (
    read_configuration_from_file_given_in_env_var,
)
from byceps.util.jobqueue import get_queue
from byceps.util.sentry import configure_sentry_from_env


@click.command()
def worker() -> None:
    """Start a worker."""
    configure_sentry_from_env('worker')

    config = read_configuration_from_file_given_in_env_var()
    config_overrides = convert_config(config)

    app = create_worker_app(config_overrides=config_overrides)

    with app.app_context():
        queues = [get_queue(app)]

        worker = Worker(queues)
        worker.work(with_scheduler=True)
