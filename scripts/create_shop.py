#!/usr/bin/env python

"""Create a shop with article and order sequences.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.shop.sequence.service import create_sequence
from byceps.services.shop.sequence.transfer.models import Purpose
from byceps.services.shop.shop import service as shop_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
@click.argument('shop_id',)
@click.argument('title')
@click.argument('email_config_id',)
@click.argument('article_prefix')
@click.argument('order_prefix')
def execute(shop_id, title, email_config_id, article_prefix, order_prefix):
    shop = shop_service.create_shop(shop_id, title, email_config_id)

    create_sequence(shop.id, Purpose.article, article_prefix)
    create_sequence(shop.id, Purpose.order, order_prefix)

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
