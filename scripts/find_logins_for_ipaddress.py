#!/usr/bin/env python

"""Find user login log entries for an IP address.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

import click

from byceps.database import db
from byceps.services.user.dbmodels.log import UserLogEntry as DbUserLogEntry
from byceps.services.user import service as user_service
from byceps.services.user.transfer.models import User
from byceps.typing import PartyID, UserID

from _util import call_with_app_context


@click.command()
@click.argument('ip_address')
def execute(ip_address: str) -> None:
    log_entries = find_log_entries(ip_address)
    users_by_id = get_users_by_id(log_entries)

    for log_entry in log_entries:
        user = users_by_id[log_entry.user_id]
        click.echo(f'{log_entry.occurred_at}\t{ip_address}\t{user.screen_name}')


def find_log_entries(ip_address: str) -> list[DbUserLogEntry]:
    return db.session \
        .query(DbUserLogEntry) \
        .filter_by(event_type='user-logged-in') \
        .filter(DbUserLogEntry.data['ip_address'].astext == ip_address) \
        .order_by(DbUserLogEntry.occurred_at) \
        .all()


def get_users_by_id(log_entries: list[DbUserLogEntry]) -> dict[UserID, User]:
    user_ids = {log_entry.user_id for log_entry in log_entries}
    users = user_service.get_users(user_ids)
    return user_service.index_users_by_id(users)


if __name__ == '__main__':
    call_with_app_context(execute)
