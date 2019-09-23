#!/usr/bin/env python

"""Generate the SQL statements to remove a user and his/her various
traces from the database.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context
from _validators import validate_user_screen_name


@click.command()
@click.argument('user', callback=validate_user_screen_name)
def execute(user):
    statements = generate_delete_statements(user.id)
    for statement in statements:
        print(statement)


def generate_delete_statements(user_id):
    for table, user_id_column in [
        ('authn_credentials', 'user_id'),
        ('authn_session_tokens', 'user_id'),
        ('authz_user_roles', 'user_id'),
        ('board_categories_lastviews', 'user_id'),
        ('board_topics_lastviews', 'user_id'),
        ('newsletter_subscription_updates', 'user_id'),
        ('consents', 'user_id'),
        ('verification_tokens', 'user_id'),
        ('user_details', 'user_id'),
        ('user_events', 'user_id'),
        ('users', 'id'),
    ]:
        yield f"DELETE FROM {table} WHERE {user_id_column} = '{user_id}';"


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
