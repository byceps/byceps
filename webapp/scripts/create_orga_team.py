#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Create an organizer team.

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.database import db

from bootstrap.helpers import create_orga_team
from bootstrap.util import app_context, get_config_name_from_env
from bootstrap.validators import validate_party


@click.command()
@click.argument('party', callback=validate_party)
@click.argument('title')
def execute(party, title):
    click.echo('Creating orga team "{}" for party "{}" ... '.format(title, party.title), nl=False)
    create_orga_team(party, title)
    db.session.commit()
    click.secho('done.', fg='green')


if __name__ == '__main__':
    config_name = get_config_name_from_env()
    with app_context(config_name):
        execute()
