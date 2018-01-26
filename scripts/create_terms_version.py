#!/usr/bin/env python

"""Create a new terms of service version.

However, do not set the new version as the current version for the brand.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.database import db
from byceps.services.terms import service as terms_service
from byceps.util.system import get_config_filename_from_env_or_exit

from bootstrap.util import app_context
from bootstrap.validators import validate_brand, validate_user_screen_name


@click.command()
@click.argument('brand', callback=validate_brand)
@click.argument('creator', callback=validate_user_screen_name)
@click.argument('title')
@click.argument('f', type=click.File())
def execute(brand, creator, title, f):
    body = f.read()

    terms_service.create_version(brand.id, creator.id, title, body)
    db.session.commit()

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
