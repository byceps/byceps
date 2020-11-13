#!/usr/bin/env python

"""Delete login user events older than a given number of days.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, timedelta

import click

from byceps.database import db
from byceps.services.user.models.event import UserEvent as DbUserEvent
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
@click.option(
    '--dry-run', is_flag=True, help='count but do not delete affected records',
)
@click.argument('minimum_age_in_days', type=int)
def execute(dry_run, minimum_age_in_days):
    latest_occurred_at = get_latest_occurred_at(minimum_age_in_days)

    click.secho(
        f'Deleting all user login events older than {minimum_age_in_days} days '
        f'(i.e. before {latest_occurred_at:%Y-%m-%d %H:%M:%S}) ...'
    )

    num_deleted = delete_user_login_events_before(latest_occurred_at, dry_run)

    click.secho(f'{num_deleted} user login events deleted.')

    if dry_run:
        click.secho(
            f'This was a dry run; no records have been deleted.', fg='yellow'
        )


def get_latest_occurred_at(minimum_age_in_days: int) -> datetime:
    now = datetime.utcnow()
    return now - timedelta(days=minimum_age_in_days)


def delete_user_login_events_before(
    latest_occurred_at: datetime, dry_run: bool
) -> int:
    num_deleted = DbUserEvent.query \
        .filter_by(event_type='user-logged-in') \
        .filter(DbUserEvent.occurred_at <= latest_occurred_at) \
        .delete()

    if not dry_run:
        db.session.commit()

    return num_deleted


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
