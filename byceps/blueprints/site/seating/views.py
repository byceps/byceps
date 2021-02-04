"""
byceps.blueprints.site.seating.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from ....services.party import service as party_service
from ....services.seating import area_service as seating_area_service
from ....services.seating.models.seat import Seat
from ....services.seating import seat_service
from ....services.seating.transfer.models import SeatID
from ....services.ticketing.models.ticket import Ticket as DbTicket
from ....services.ticketing import (
    exceptions as ticket_exceptions,
    ticket_seat_management_service,
    ticket_service,
)
from ....services.ticketing.transfer.models import TicketID
from ....util.authorization import register_permission_enum
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import login_required, redirect_to, respond_no_content

from ...admin.seating.authorization import SeatingPermission

from . import service


blueprint = create_blueprint('seating', __name__)


register_permission_enum(SeatingPermission)


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

    users_by_id = service.get_users(seats, [])

    seats = service.get_seats(seats, users_by_id)

    return {
        'area': area,
        'seat_management_enabled': seat_management_enabled,
        'seats': seats,
        'manage_mode': False,
    }


@blueprint.route('/areas/<slug>/manage_seats')
@login_required
@templated('site/seating/view_area')
def manage_seats_in_area(slug):
    """Manage seats for assigned tickets in area."""
    if not _is_seat_management_enabled():
        flash_error(
            gettext('Seat reservations cannot be changed at this time.')
        )
        return redirect_to('.view_area', slug=slug)

    area = seating_area_service.find_area_for_party_by_slug(g.party_id, slug)
    if area is None:
        abort(404)

    seat_management_enabled = _is_seat_management_enabled()

    seat_manager_id = None
    selected_ticket_id = None
    selected_ticket = None

    if _is_current_user_seating_admin():
        selected_ticket = _get_selected_ticket()
        if selected_ticket is not None:
            seat_manager_id = selected_ticket.get_seat_manager().id
            selected_ticket_id = selected_ticket.id
        elif seat_management_enabled:
            seat_manager_id = g.user.id

    elif seat_management_enabled:
        seat_manager_id = g.user.id

    seats = seat_service.get_seats_with_tickets_for_area(area.id)

    if seat_manager_id is not None:
        tickets = ticket_service.find_tickets_for_seat_manager(
            seat_manager_id, g.party_id
        )
    else:
        tickets = []

    users_by_id = service.get_users(seats, tickets)

    seats = service.get_seats(seats, users_by_id)

    if seat_management_enabled:
        managed_tickets = list(
            service.get_managed_tickets(tickets, users_by_id)
        )
    else:
        managed_tickets = []

    return {
        'area': area,
        'seats': seats,
        'manage_mode': True,
        'seat_management_enabled': seat_management_enabled,
        'managed_tickets': managed_tickets,
        'selected_ticket_id': selected_ticket_id,
    }


def _get_selected_ticket():
    selected_ticket = None

    selected_ticket_id_arg = request.args.get('ticket_id')
    if selected_ticket_id_arg:
        selected_ticket = ticket_service.find_ticket(selected_ticket_id_arg)
        if selected_ticket is None:
            flash_error(
                gettext(
                    'Ticket ID "%(selected_ticket_id_arg)s" not found.',
                    selected_ticket_id_arg=selected_ticket_id_arg,
                )
            )

    if (selected_ticket is not None) and selected_ticket.revoked:
        flash_error(
            gettext(
                'Ticket "%(selected_ticket_code)s" is revoked.',
                selected_ticket_code=selected_ticket.code,
            )
        )
        selected_ticket = None

    return selected_ticket


@blueprint.route(
    '/ticket/<uuid:ticket_id>/seat/<uuid:seat_id>', methods=['POST']
)
@login_required
@respond_no_content
def occupy_seat(ticket_id, seat_id):
    """Use ticket to occupy seat."""
    if not _is_seat_management_enabled():
        flash_error(
            gettext('Seat reservations cannot be changed at this time.')
        )
        return

    ticket = _get_ticket_or_404(ticket_id)

    manager = g.user

    if (
        not ticket.is_seat_managed_by(manager.id)
        and not _is_current_user_seating_admin()
    ):
        flash_error(
            gettext(
                'You are not authorized to manage the seat for ticket %(ticket_code)s.',
                ticket_code=ticket.code,
            )
        )
        return

    seat = _get_seat_or_404(seat_id)

    if seat.is_occupied:
        flash_error(
            gettext(
                '%(seat_label)s is already occupied.', seat_label=seat.label
            )
        )
        return

    try:
        ticket_seat_management_service.occupy_seat(
            ticket.id, seat.id, manager.id
        )
    except ticket_exceptions.SeatChangeDeniedForBundledTicket:
        flash_error(
            gettext(
                'Ticket %(ticket_code)s belongs to a bundle and cannot be managed separately.',
                ticket_code=ticket.code,
            )
        )
        return
    except ticket_exceptions.TicketCategoryMismatch:
        flash_error(
            gettext(
                'Ticket %(ticket_code)s and seat "%(seat_label)s" belong to different categories.',
                ticket_code=ticket.code,
                seat_label=seat.label,
            )
        )
        return
    except ValueError:
        abort(404)

    flash_success(
        gettext(
            '%(seat_label)s has been occupied with ticket %(ticket_code)s.',
            seat_label=seat.label,
            ticket_code=ticket.code,
        )
    )


@blueprint.route('/ticket/<uuid:ticket_id>/seat', methods=['DELETE'])
@login_required
@respond_no_content
def release_seat(ticket_id):
    """Release the seat."""
    if not _is_seat_management_enabled():
        flash_error(
            gettext('Seat reservations cannot be changed at this time.')
        )
        return

    ticket = _get_ticket_or_404(ticket_id)

    if not ticket.occupied_seat:
        flash_error(
            gettext(
                'Ticket %(ticket_code)s occupies no seat.',
                ticket_code=ticket.code,
            )
        )
        return

    manager = g.user

    if (
        not ticket.is_seat_managed_by(manager.id)
        and not _is_current_user_seating_admin()
    ):
        flash_error(
            gettext(
                'You are not authorized to manage the seat for ticket %(ticket_code)s.',
                ticket_code=ticket.code,
            )
        )
        return

    seat = ticket.occupied_seat

    try:
        ticket_seat_management_service.release_seat(ticket.id, manager.id)
    except ticket_exceptions.SeatChangeDeniedForBundledTicket:
        flash_error(
            gettext(
                'Ticket %(ticket_code)s belongs to a bundle and cannot be managed separately.',
                ticket_code=ticket.code,
            )
        )
        return

    flash_success(
        gettext('%(seat_label)s has been released.', seat_label=seat.label)
    )


def _is_seat_management_enabled():
    if not g.user.authenticated:
        return False

    if g.party_id is None:
        return False

    if _is_current_user_seating_admin():
        return True

    party = party_service.get_party(g.party_id)
    return party.seat_management_enabled


def _is_current_user_seating_admin() -> bool:
    return g.user.has_permission(SeatingPermission.administrate)


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
