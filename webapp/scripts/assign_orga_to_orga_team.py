#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Assign a user to an organizer team.

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.database import db

from bootstrap.helpers import assign_user_to_orga_team, get_orga_team, \
    get_user
from bootstrap.util import app_context, get_config_name_from_env
from bootstrap.validators import validate_party


@click.command()
@click.argument('party', callback=validate_party)
@click.argument('screen_name')
@click.argument('team_id')
def execute(party, screen_name, team_id):
    user = get_user(screen_name)
    team = get_orga_team(team_id)

    click.echo('Assigning user "{}" to team "{}" … '.format(screen_name, team.title), nl=False)

    assign_user_to_orga_team(user, team, party)
    db.session.commit()

    click.secho('done.', fg='green')


if __name__ == '__main__':
    config_name = get_config_name_from_env()
    with app_context(config_name):
        execute()
