#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Promote a user to organizer status.

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.database import db

from bootstrap.helpers import get_user, promote_orga
from bootstrap.util import app_context, get_config_name_from_env
from bootstrap.validators import validate_brand


@click.command()
@click.argument('brand', callback=validate_brand)
@click.argument('screen_name')
def execute(brand, screen_name):
    click.echo('Promoting user "{}" to orga for brand {} ... '
               .format(screen_name, brand.title), nl=False)

    user = get_user(screen_name)
    promote_orga(brand, user)
    db.session.commit()

    click.secho('done.', fg='green')


if __name__ == '__main__':
    config_name = get_config_name_from_env()
    with app_context(config_name):
        execute()
