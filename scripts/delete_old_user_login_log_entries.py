#!/usr/bin/env python

"""Delete login user log entries older than a given number of days.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, timedelta

import click

from byceps.services.user import user_log_service

from _util import call_with_app_context


@click.command()
@click.argument('minimum_age_in_days', type=int)
def execute(minimum_age_in_days) -> None:
    now = datetime.utcnow()
    occurred_before = now - timedelta(days=minimum_age_in_days)

    click.secho(
        'Deleting all user login log entries '
        f'older than {minimum_age_in_days} days '
        f'(i.e. before {occurred_before:%Y-%m-%d %H:%M:%S}) ...'
    )

    num_deleted = user_log_service.delete_login_entries(occurred_before)

    click.secho(f'{num_deleted} user login log entries deleted.')


if __name__ == '__main__':
    call_with_app_context(execute)
