"""
byceps.blueprints.seating.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Optional, Sequence

from flask import abort, g, request

from ...config import get_seat_management_enabled, get_ticket_management_enabled
from ...services.seating import area_service as seating_area_service
from ...services.seating.models.seat import Seat, SeatID
from ...services.seating import seat_service
from ...services.ticketing.models.ticket import Ticket, TicketID
from ...services.ticketing import ticket_service
from ...services.user.models.user import UserTuple
from ...services.user import service as user_service
from ...typing import UserID
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_error, flash_success
from ...util.framework.templating import templated
from ...util.views import respond_no_content


blueprint = create_blueprint('seating', __name__)


@blueprint.route('/')
@templated
def index():
    """List areas."""
    areas = seating_area_service.get_areas_for_party(g.party_id)

    return {
        'areas': areas,
    }


@blueprint.route('/areas/<slug>')
@templated
def view_area(slug):
    """View area."""
    area = seating_area_service.find_area_for_party_by_slug(g.party_id, slug)
    if area is None:
        abort(404)

    seat_management_enabled = get_seat_management_enabled()
    ticket_management_enabled = get_ticket_management_enabled()

    seats = []

    if ticket_management_enabled:
        tickets = ticket_service.find_tickets_for_seat_manager(
            g.current_user.id, g.party_id)
    else:
        tickets = None

    current_ticket_id = _find_current_ticket_id()

    users_by_id = _get_users(seats, tickets)

    return {
        'area': area,
        'seat_management_enabled': seat_management_enabled,
        'ticket_management_enabled': ticket_management_enabled,
        'seats': seats,
        'tickets': tickets,
        'current_ticket_id': current_ticket_id,
        'users_by_id': users_by_id,
    }


def _find_current_ticket_id() -> Optional[TicketID]:
    ticket_code = request.args.get('ticket')
    if ticket_code is None:
        return None

    ticket = ticket_service.find_ticket_by_code(ticket_code)
    if ticket is None:
        flash_error('Unbekannte Ticket-ID')
        return None

    if not ticket.is_seat_managed_by(g.current_user.id):
        flash_error(
            'Du bist nicht berechtigt, den Sitzplatz '
            'für Ticket {} zu verwalten.',
            ticket.code)
        return None

    return ticket.id


def _get_users(seats: Sequence[Seat], tickets: Sequence[Ticket]
              ) -> Dict[UserID, UserTuple]:
    user_ids = set()

    for seat in seats:
        if seat.has_user:
            user_ids.add(seat.occupied_by_ticket.used_by_id)

    for ticket in tickets:
        user_id = ticket.used_by_id
        if user_id is not None:
            user_ids.add(user_id)

    users = user_service.find_users(user_ids)
    return user_service.index_users_by_id(users)


@blueprint.route('/ticket/<uuid:ticket_id>/seat/<uuid:seat_id>', methods=['POST'])
@respond_no_content
def occupy_seat(ticket_id, seat_id):
    """Use ticket to occupy seat."""
    _abort_if_seat_management_disabled()

    ticket = _get_ticket_or_404(ticket_id)

    manager = g.current_user

    if not ticket.is_seat_managed_by(manager.id):
        abort(403)

    seat = _get_seat_or_404(seat_id)

    if seat.is_occupied:
        abort(403)

    ticket_service.occupy_seat(ticket.id, seat.id, manager.id)

    flash_success('{} wurde mit Ticket {} reserviert.', seat.label, ticket.code)


@blueprint.route('/ticket/<uuid:ticket_id>/seat', methods=['DELETE'])
@respond_no_content
def release_seat(ticket_id):
    """Release the seat."""
    _abort_if_seat_management_disabled()

    ticket = _get_ticket_or_404(ticket_id)

    if not ticket.occupied_seat:
        abort(404)

    manager = g.current_user

    if not ticket.is_seat_managed_by(manager.id):
        abort(403)

    seat = ticket.occupied_seat

    ticket_service.release_seat(ticket.id, manager.id)

    flash_success('{} wurde freigegeben.', seat.label)


def _abort_if_seat_management_disabled() -> None:
    if not get_seat_management_enabled():
        flash_error('Sitzplätze können derzeit nicht verändert werden.')
        abort(403)


def _get_ticket_or_404(ticket_id: TicketID) -> Ticket:
    ticket = ticket_service.find_ticket(ticket_id)

    if (ticket is None) or ticket.revoked:
        abort(404)

    return ticket


def _get_seat_or_404(seat_id: SeatID) -> Seat:
    seat = seat_service.find_seat(seat_id)

    if seat is None:
        abort(404)

    return seat
