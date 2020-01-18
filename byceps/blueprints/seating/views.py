"""
byceps.blueprints.seating.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Iterator, Sequence

from flask import abort, g

from ...services.party import service as party_service
from ...services.seating import area_service as seating_area_service
from ...services.seating.models.seat import Seat
from ...services.seating import seat_service
from ...services.seating.transfer.models import SeatID
from ...services.ticketing.models.ticket import Ticket as DbTicket
from ...services.ticketing import (
    exceptions as ticket_exceptions,
    ticket_seat_management_service,
    ticket_service,
)
from ...services.ticketing.transfer.models import TicketID
from ...services.user import service as user_service
from ...services.user.transfer.models import User
from ...typing import UserID
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_error, flash_success
from ...util.framework.templating import templated
from ...util.views import respond_no_content

from ..authentication.decorators import login_required


blueprint = create_blueprint('seating', __name__)


@blueprint.route('/')
@templated
def index():
    """List areas."""
    if g.party_id is None:
        # No party is configured for the current site.
        abort(404)

    areas = seating_area_service.get_areas_for_party(g.party_id)

    return {
        'areas': areas,
    }


@blueprint.route('/areas/<slug>')
@templated
def view_area(slug):
    """View area."""
    if g.party_id is None:
        # No party is configured for the current site.
        abort(404)

    area = seating_area_service.find_area_for_party_by_slug(g.party_id, slug)
    if area is None:
        abort(404)

    seat_management_enabled = _is_seat_management_enabled()

    seats = seat_service.get_seats_with_tickets_for_area(area.id)

    if seat_management_enabled:
        managed_tickets = ticket_service.find_tickets_for_seat_manager(
            g.current_user.id, g.party_id
        )
    else:
        managed_tickets = []

    users_by_id = _get_users(seats, managed_tickets)

    return {
        'area': area,
        'seat_management_enabled': seat_management_enabled,
        'seats': seats,
        'managed_tickets': managed_tickets,
        'users_by_id': users_by_id,
    }


@blueprint.route(
    '/ticket/<uuid:ticket_id>/seat/<uuid:seat_id>', methods=['POST']
)
@login_required
@respond_no_content
def occupy_seat(ticket_id, seat_id):
    """Use ticket to occupy seat."""
    _abort_if_seat_management_disabled()

    ticket = _get_ticket_or_404(ticket_id)

    manager = g.current_user

    if not ticket.is_seat_managed_by(manager.id):
        flash_error(
            'Du bist nicht berechtigt, den Sitzplatz '
            f'für Ticket {ticket.code} zu verwalten.'
        )
        return

    seat = _get_seat_or_404(seat_id)

    if seat.is_occupied:
        flash_error(f'{seat.label} ist bereits belegt.')
        return

    try:
        ticket_seat_management_service.occupy_seat(
            ticket.id, seat.id, manager.id
        )
    except ticket_exceptions.SeatChangeDeniedForBundledTicket:
        flash_error(
            f'Ticket {ticket.code} gehört zu einem Paket '
            'und kann nicht einzeln verwaltet werden.'
        )
        return
    except ticket_exceptions.TicketCategoryMismatch:
        flash_error(
            f'Ticket {ticket.code} und {seat.label} haben '
            'unterschiedliche Kategorien.'
        )
        return
    except ValueError:
        abort(404)

    flash_success(f'{seat.label} wurde mit Ticket {ticket.code} reserviert.')


@blueprint.route('/ticket/<uuid:ticket_id>/seat', methods=['DELETE'])
@login_required
@respond_no_content
def release_seat(ticket_id):
    """Release the seat."""
    _abort_if_seat_management_disabled()

    ticket = _get_ticket_or_404(ticket_id)

    if not ticket.occupied_seat:
        flash_error(f'Ticket {ticket.code} belegt keinen Sitzplatz.')
        return

    manager = g.current_user

    if not ticket.is_seat_managed_by(manager.id):
        flash_error(
            'Du bist nicht berechtigt, den Sitzplatz '
            f'für Ticket {ticket.code} zu verwalten.'
        )
        return

    seat = ticket.occupied_seat

    try:
        ticket_seat_management_service.release_seat(ticket.id, manager.id)
    except ticket_exceptions.SeatChangeDeniedForBundledTicket:
        flash_error(
            f'Ticket {ticket.code} gehört zu einem Paket '
            'und kann nicht einzeln verwaltet werden.'
        )
        return

    flash_success(f'{seat.label} wurde freigegeben.')


def _abort_if_seat_management_disabled() -> None:
    if not _is_seat_management_enabled():
        flash_error('Sitzplätze können derzeit nicht verändert werden.')
        return


def _is_seat_management_enabled():
    if g.current_user.is_anonymous:
        return False

    if g.party_id is None:
        return False

    party = party_service.get_party(g.party_id)
    return party.seat_management_enabled


def _get_ticket_or_404(ticket_id: TicketID) -> DbTicket:
    ticket = ticket_service.find_ticket(ticket_id)

    if (ticket is None) or ticket.revoked:
        abort(404)

    return ticket


def _get_seat_or_404(seat_id: SeatID) -> Seat:
    seat = seat_service.find_seat(seat_id)

    if seat is None:
        abort(404)

    return seat
