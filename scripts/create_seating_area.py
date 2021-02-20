#!/usr/bin/env python

"""Create a seating area.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.seating import area_service

from _util import call_with_app_context
from _validators import validate_party


@click.command()
@click.argument('party', callback=validate_party)
@click.argument('slug')
@click.argument('title')
def execute(party, slug, title):
    area_service.create_area(party.id, slug, title)
    click.secho('Done.', fg='green')


if __name__ == '__main__':
    call_with_app_context(execute)
