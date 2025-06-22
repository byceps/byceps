"""Occupy a seat group with a ticket bundle.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from _util import call_with_app_context
import click

from byceps.services.seating import seat_group_service
from byceps.services.seating.models import SeatGroup, SeatGroupID
from byceps.services.ticketing import ticket_bundle_service
from byceps.services.ticketing.dbmodels.ticket_bundle import DbTicketBundle
from byceps.services.ticketing.models.ticket import TicketBundleID


def validate_seat_group(ctx, param, seat_group_id_value: str) -> SeatGroup:
    try:
        seat_group_id = SeatGroupID(UUID(seat_group_id_value))
    except ValueError as exc:
        raise click.BadParameter(
            f'Invalid seat group ID "{seat_group_id_value}": {exc}'
        ) from exc

    seat_group = seat_group_service.find_seat_group(seat_group_id)

    if not seat_group:
        raise click.BadParameter(f'Unknown seat group ID "{seat_group_id}".')

    return seat_group


def validate_ticket_bundle(
    ctx, param, ticket_bundle_id_value: str
) -> DbTicketBundle:
    try:
        ticket_bundle_id = TicketBundleID(UUID(ticket_bundle_id_value))
    except ValueError as exc:
        raise click.BadParameter(
            f'Invalid ticket bundle ID "{ticket_bundle_id_value}": {exc}'
        ) from exc

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
    occupy_result = seat_group_service.occupy_seat_group(
        seat_group, ticket_bundle
    )

    if occupy_result.is_err():
        error_str = occupy_result.unwrap_err().message
        click.secho(
            f'Group "{seat_group.title}" could not be occupied: {error_str}',
            fg='red',
        )
        return

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    call_with_app_context(execute)
