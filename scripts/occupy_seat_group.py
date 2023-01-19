#!/usr/bin/env python

"""Occupy a seat group with a ticket bundle.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

import click

from byceps.services.seating.dbmodels.seat_group import DbSeatGroup
from byceps.services.seating import seat_group_service
from byceps.services.seating.transfer.models import SeatGroupID
from byceps.services.ticketing.dbmodels.ticket_bundle import DbTicketBundle
from byceps.services.ticketing.models.ticket import TicketBundleID
from byceps.services.ticketing import ticket_bundle_service

from _util import call_with_app_context


def validate_seat_group(ctx, param, seat_group_id_value: str) -> DbSeatGroup:
    try:
        seat_group_id = SeatGroupID(UUID(seat_group_id_value))
    except ValueError as e:
        raise click.BadParameter(
            f'Invalid seat group ID "{seat_group_id_value}": {e}'
        )

    seat_group = seat_group_service.find_seat_group(seat_group_id)

    if not seat_group:
        raise click.BadParameter(f'Unknown seat group ID "{seat_group_id}".')

    return seat_group


def validate_ticket_bundle(
    ctx, param, ticket_bundle_id_value: str
) -> DbTicketBundle:
    try:
        ticket_bundle_id = TicketBundleID(UUID(ticket_bundle_id_value))
    except ValueError as e:
        raise click.BadParameter(
            f'Invalid ticket bundle ID "{ticket_bundle_id_value}": {e}'
        )

    ticket_bundle = ticket_bundle_service.find_bundle(ticket_bundle_id)

    if not ticket_bundle:
        raise click.BadParameter(
            f'Unknown ticket bundle ID "{ticket_bundle_id}".'
        )

    return ticket_bundle


@click.command()
@click.argument('seat_group', callback=validate_seat_group)
@click.argument('ticket_bundle', callback=validate_ticket_bundle)
def execute(seat_group, ticket_bundle) -> None:
    seat_group_service.occupy_seat_group(seat_group, ticket_bundle)

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    call_with_app_context(execute)
