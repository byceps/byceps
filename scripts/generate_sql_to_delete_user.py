#!/usr/bin/env python

"""Generate the SQL statements to remove one or more users and their
various (but not all) traces from the database.

Might fail for example if a user posted in a discussion board.

Run script `clean_up_after_deleted_users.py` before this one.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterable, Iterator

import click

from byceps.services.user import user_service
from byceps.typing import UserID

from _util import call_with_app_context
from _validators import validate_user_id_format


def validate_user_ids(ctx, param, user_ids: Iterable[str]) -> list[UserID]:
    def _validate() -> Iterator[UserID]:
        for user_id in user_ids:
            yield validate_user_id_format(ctx, param, user_id)

    return list(_validate())


@click.command()
@click.argument('user_ids', callback=validate_user_ids, nargs=-1, required=True)
def execute(user_ids) -> None:
    statements = generate_delete_statements_for_users(user_ids)
    for statement in statements:
        print(statement)


def generate_delete_statements_for_users(
    user_ids: Iterable[UserID],
) -> Iterator[str]:
    users = user_service.get_users(set(user_ids))
    existing_user_ids = {u.id for u in users}

    for user_id in user_ids:
        if user_id not in existing_user_ids:
            click.secho(
                # Mask as SQL comment in case STDERR output, is copied and
                # pasted/piped with the actual SQL statements into a RDBMS.
                f'-- Skipping unknown user ID "{user_id}".\n',
                fg='yellow',
                err=True,
            )
            continue

        yield from generate_delete_statements_for_user(user_id)
        yield ''  # empty line


def generate_delete_statements_for_user(user_id: UserID) -> Iterator[str]:
    for table, user_id_column in [
        ('user_details', 'user_id'),
        ('user_log_entries', 'user_id'),
        ('users', 'id'),
    ]:
        yield f"DELETE FROM {table} WHERE {user_id_column} = '{user_id}';"


if __name__ == '__main__':
    call_with_app_context(execute)
