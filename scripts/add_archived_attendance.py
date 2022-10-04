#!/usr/bin/env python

"""Add the attendance of a user at a party to the archive.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.ticketing import ticket_attendance_service

from _util import call_with_app_context
from _validators import validate_party, validate_user_id


@click.command()
@click.argument('user', callback=validate_user_id)
@click.argument('party', callback=validate_party)
def execute(user, party) -> None:
    click.echo(
        f'Adding attendance of user "{user.screen_name}" '
        f'at party "{party.title}" ... ',
        nl=False,
    )

    ticket_attendance_service.create_archived_attendance(user.id, party.id)

    click.secho('done.', fg='green')


if __name__ == '__main__':
    call_with_app_context(execute)
