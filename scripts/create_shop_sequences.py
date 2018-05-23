#!/usr/bin/env python

"""Create article and order sequences for a party's shop.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.shop.sequence.models import Purpose
from byceps.services.shop.sequence.service import create_party_sequence
from byceps.util.system import get_config_filename_from_env_or_exit

from bootstrap.util import app_context
from bootstrap.validators import validate_party


@click.command()
@click.argument('party', callback=validate_party)
@click.argument('article_prefix')
@click.argument('order_prefix')
def execute(party, article_prefix, order_prefix):
    create_party_sequence(party.id, Purpose.article, article_prefix)
    create_party_sequence(party.id, Purpose.order, order_prefix)

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
