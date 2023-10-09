#!/usr/bin/env python

"""Find user login log entries for an IP address.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.authn.session import authn_session_service
from byceps.services.user import user_service

from _util import call_with_app_context


@click.command()
@click.argument('ip_address')
def execute(ip_address: str) -> None:
    occurred_at_and_user_ids = authn_session_service.find_logins_for_ip_address(
        ip_address
    )

    user_ids = {user_id for _, user_id in occurred_at_and_user_ids}
    users_by_id = user_service.get_users_indexed_by_id(user_ids)

    occurred_at_and_users = [
        (occurred_at, users_by_id[user_id])
        for occurred_at, user_id in occurred_at_and_user_ids
    ]

    for occurred_at, user in occurred_at_and_users:
        click.echo(f'{occurred_at}\t{ip_address}\t{user.screen_name}')


if __name__ == '__main__':
    call_with_app_context(execute)
