#!/usr/bin/env python

"""Occupy a seat group with a ticket bundle.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.seating import seat_group_service
from byceps.services.ticketing import ticket_bundle_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


def get_seat_group(ctx, param, seat_group_id):
    seat_group = seat_group_service.find_seat_group(seat_group_id)

    if not seat_group:
        raise click.BadParameter(f'Unknown seat group ID "{seat_group_id}".')

    return seat_group


def get_ticket_bundle(ctx, param, ticket_bundle_id):
    ticket_bundle = ticket_bundle_service.find_bundle(ticket_bundle_id)

    if not ticket_bundle:
        raise click.BadParameter(
            f'Unknown ticket bundle ID "{ticket_bundle_id}".'
        )

    return ticket_bundle


@click.command()
@click.argument('seat_group', callback=get_seat_group)
@click.argument('ticket_bundle', callback=get_ticket_bundle)
def execute(seat_group, ticket_bundle):
    seat_group_service.occupy_seat_group(seat_group, ticket_bundle)

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
