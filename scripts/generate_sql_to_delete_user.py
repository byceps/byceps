#!/usr/bin/env python

"""Generate the SQL statements to remove one or more users and they
various traces from the database.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context
from _validators import validate_user_id


def validate_user_ids(ctx, param, user_ids):
    def _validate():
        for user_id in user_ids:
            yield validate_user_id(ctx, param, user_id)

    return list(_validate())


@click.command()
@click.argument('users', callback=validate_user_ids, nargs=-1, required=True)
def execute(users):
    statements = generate_delete_statements_for_users(users)
    for statement in statements:
        print(statement)


def generate_delete_statements_for_users(users):
    for user in users:
        yield from generate_delete_statements_for_user(user.id)
        yield ''  # empty line


def generate_delete_statements_for_user(user_id):
    for table, user_id_column in [
        ('authn_credentials', 'user_id'),
        ('authn_session_tokens', 'user_id'),
        ('authz_user_roles', 'user_id'),
        ('board_categories_lastviews', 'user_id'),
        ('board_topics_lastviews', 'user_id'),
        ('newsletter_subscription_updates', 'user_id'),
        ('consents', 'user_id'),
        ('verification_tokens', 'user_id'),
        ('user_avatar_selections', 'user_id'),
        ('user_avatars', 'creator_id'),
        ('user_details', 'user_id'),
        ('user_events', 'user_id'),
        ('users', 'id'),
    ]:
        yield f"DELETE FROM {table} WHERE {user_id_column} = '{user_id}';"


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
