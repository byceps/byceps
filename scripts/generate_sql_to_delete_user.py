#!/usr/bin/env python
"""Generate the SQL statements to remove a user and his/her various
traces from the database.

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.util.system import get_config_filename_from_env_or_exit

from bootstrap.util import app_context
from bootstrap.validators import validate_user_screen_name


@click.command()
@click.argument('user', callback=validate_user_screen_name)
def execute(user):
    click.echo('Generating SQL statements to delete user "{}" ...'.format(user.screen_name))

    statements = generate_delete_statements(user.id)
    for statement in statements:
        click.secho(statement, fg='red')


def generate_delete_statements(user_id):
    for table, user_id_column in [
        ('authn_credentials', 'user_id'),
        ('authn_session_tokens', 'user_id'),
        ('authz_user_roles', 'user_id'),
        ('board_categories_lastviews', 'user_id'),
        ('board_topics_lastviews', 'user_id'),
        ('newsletter_subscriptions', 'user_id'),
        ('terms_consents', 'user_id'),
        ('verification_tokens', 'user_id'),
        ('user_details', 'user_id'),
        ('users', 'id'),
    ]:
        yield "DELETE FROM {} WHERE {} = '{}';".format(
            table, user_id_column, user_id)


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
