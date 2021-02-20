#!/usr/bin/env python

"""Log out users by removing their session tokens.

This is meant to be used when new terms of service are published so
users have to log in again and are presented the form to accept the new
terms of service.

Sessions will be recreated on demand after successful login.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.authentication.session import service as session_service

from _util import call_with_app_context


@click.command()
def execute():
    click.secho('Removing all user sessions ... ', nl=False)

    deleted_total = session_service.delete_all_session_tokens()
    click.secho(f'{deleted_total} sessions removed.', fg='green')


if __name__ == '__main__':
    call_with_app_context(execute)
