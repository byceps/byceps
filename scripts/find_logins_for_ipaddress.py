#!/usr/bin/env python

"""Find user login log entries for an IP address.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime

import click
from sqlalchemy import select

from byceps.database import db
from byceps.services.user.dbmodels.log import UserLogEntry as DbUserLogEntry
from byceps.services.user import service as user_service
from byceps.services.user.transfer.models import User
from byceps.typing import PartyID, UserID

from _util import call_with_app_context


@click.command()
@click.argument('ip_address')
def execute(ip_address: str) -> None:
    occurred_at_and_user_ids = find_log_entries(ip_address)

    users_by_id = get_users_by_id(occurred_at_and_user_ids)
    occurred_at_and_users = [
        (occurred_at, users_by_id[user_id])
        for occurred_at, user_id in occurred_at_and_user_ids
    ]

    for occurred_at, user in occurred_at_and_users:
        click.echo(f'{occurred_at}\t{ip_address}\t{user.screen_name}')


def find_log_entries(ip_address: str) -> list[tuple[datetime, UserID]]:
    return db.session.execute(
        select(
            DbUserLogEntry.occurred_at,
            DbUserLogEntry.user_id,
        )
        .filter_by(event_type='user-logged-in')
        .filter(DbUserLogEntry.data['ip_address'].astext == ip_address)
        .order_by(DbUserLogEntry.occurred_at)
    ).all()


def get_users_by_id(
    occurred_at_and_user_ids: list[tuple[datetime, UserID]]
) -> dict[UserID, User]:
    user_ids = {user_id for _, user_id in occurred_at_and_user_ids}
    users = user_service.get_users(user_ids)
    return user_service.index_users_by_id(users)


if __name__ == '__main__':
    call_with_app_context(execute)
