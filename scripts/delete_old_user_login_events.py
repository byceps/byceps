#!/usr/bin/env python

"""Delete login user events older than a given number of days.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, timedelta

import click

from byceps.services.user import event_service as user_event_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
@click.argument('minimum_age_in_days', type=int)
def execute(minimum_age_in_days):
    now = datetime.utcnow()
    occurred_before = now - timedelta(days=minimum_age_in_days)

    click.secho(
        f'Deleting all user login events older than {minimum_age_in_days} days '
        f'(i.e. before {occurred_before:%Y-%m-%d %H:%M:%S}) ...'
    )

    num_deleted = user_event_service.delete_user_login_events(occurred_before)

    click.secho(f'{num_deleted} user login events deleted.')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
