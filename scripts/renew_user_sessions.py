#!/usr/bin/env python

"""Log out users by renewing their session tokens.

This is meant to be used when new terms of service are published so
users have to log in again and are presented the form to accept the new
terms of service.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

import click

from byceps.database import db
from byceps.services.authentication.session import service as session_service
from byceps.services.user.models.user import User
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
def execute():
    user_ids = {u.id for u in find_enabled_users()}

    renew_session_tokens(user_ids)

    click.secho('Done.', fg='green')


def find_enabled_users():
    return User.query.filter_by(enabled=True).all()


def renew_session_tokens(user_ids):
    now = datetime.utcnow()

    for user_id in user_ids:
        renew_session_token(user_id, now)
        print('.', end='', flush=True)
    print()

    db.session.commit()


def renew_session_token(user_id, updated_at):
    token = session_service.find_session_token_for_user(user_id)
    session_service.update_session_token(token, updated_at)


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
