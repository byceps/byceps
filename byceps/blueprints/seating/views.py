"""
byceps.blueprints.seating.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ...config import get_seat_management_enabled, get_ticket_management_enabled
from ...services.seating import area_service as seating_area_service
from ...services.seating.models.seat import Seat, SeatID
from ...services.seating import seat_service
from ...services.ticketing.models.ticket import Ticket, TicketID
from ...services.ticketing import ticket_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_success
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

    return {
        'area': area,
        'seat_management_enabled': seat_management_enabled,
        'ticket_management_enabled': ticket_management_enabled,
    }


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
