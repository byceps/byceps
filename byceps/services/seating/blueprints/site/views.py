"""
byceps.services.seating.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Any

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.seating import (
    seat_reservation_service,
    seat_service,
    seating_area_service,
)
from byceps.services.seating.models import Seat, SeatID, SeatingArea
from byceps.services.site.blueprints.site.navigation import (
    subnavigation_for_view,
)
from byceps.services.ticketing import (
    errors as ticketing_errors,
    ticket_seat_management_service,
    ticket_service,
)
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import TicketID
from byceps.util.authz import has_current_user_permission
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import login_required, redirect_to, respond_no_content


blueprint = create_blueprint('seating', __name__)


@blueprint.get('/')
@templated
@subnavigation_for_view('seating_plan')
def index():
    """List areas."""
    if not g.party:
        # No party is configured for the current site.
        abort(404)

    areas = seating_area_service.get_areas_for_party(g.party.id)
    if len(areas) == 1:
        return _render_view_area(areas[0])

    areas_with_utilization = seating_area_service.get_areas_with_utilization(
        g.party.id
    )
    if not areas_with_utilization:
        abort(404)

    seat_utilizations = [awu[1] for awu in areas_with_utilization]
    total_seat_utilization = seat_service.aggregate_seat_utilizations(
        seat_utilizations
    )

    return {
        'areas_with_utilization': areas_with_utilization,
        'total_seat_utilization': total_seat_utilization,
    }


@blueprint.get('/areas/<slug>')
def view_area(slug):
    """View area."""
    if not g.party:
        # No party is configured for the current site.
        abort(404)

    area = seating_area_service.find_area_for_party_by_slug(g.party.id, slug)
    if area is None:
        abort(404)

    return _render_view_area(area)


@templated('site/seating/view_area')
@subnavigation_for_view('seating_plan')
def _render_view_area(area: SeatingArea) -> dict[str, Any]:
    seat_management_enabled = _is_seat_management_enabled()

    seats = seat_service.get_area_seats(area.id)

    seat_utilization = seat_service.get_seat_utilization(g.party.id)

    return {
        'area': area,
        'seat_management_enabled': seat_management_enabled,
        'seats': seats,
        'seat_utilization': seat_utilization,
        'manage_mode': False,
    }


@blueprint.get('/areas/<slug>/manage_seats')
@login_required
@templated('site/seating/view_area')
@subnavigation_for_view('seating_plan')
def manage_seats_in_area(slug):
    """Manage seats for assigned tickets in area."""
    seat_management_enabled = _is_seat_management_enabled()

    if not seat_management_enabled:
        flash_error(
            gettext('Seat reservations cannot be changed at this time.')
        )
        return redirect_to('.view_area', slug=slug)

    area = seating_area_service.find_area_for_party_by_slug(g.party.id, slug)
    if area is None:
        abort(404)

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

    seats = seat_service.get_area_seats(area.id)

    if seat_management_enabled and (seat_manager_id is not None):
        managed_tickets = seat_reservation_service.get_managed_tickets(
            seat_manager_id, g.party.id
        )
    else:
        managed_tickets = []

    seat_utilization = seat_service.get_seat_utilization(g.party.id)

    return {
        'area': area,
        'seats': seats,
        'seat_utilization': seat_utilization,
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


@blueprint.post('/ticket/<uuid:ticket_id>/seat/<uuid:seat_id>')
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

    if ticket_service.find_ticket_occupying_seat(seat.id) is not None:
        flash_error(
            gettext(
                '%(seat_label)s is already occupied.', seat_label=seat.label
            )
        )
        return

    try:
        occupy_seat_result = ticket_seat_management_service.occupy_seat(
            ticket.id, seat.id, manager
        )
    except ValueError:
        abort(404)

    if occupy_seat_result.is_err():
        err = occupy_seat_result.unwrap_err()
        if isinstance(
            err, ticketing_errors.SeatChangeDeniedForBundledTicketError
        ):
            flash_error(
                gettext(
                    'Ticket %(ticket_code)s belongs to a bundle and cannot be managed separately.',
                    ticket_code=ticket.code,
                )
            )
        elif isinstance(err, ticketing_errors.TicketCategoryMismatchError):
            flash_error(
                gettext(
                    'Ticket %(ticket_code)s and seat "%(seat_label)s" belong to different categories.',
                    ticket_code=ticket.code,
                    seat_label=seat.label,
                )
            )
        else:
            flash_error(gettext('An unexpected error occurred.'))

        return

    flash_success(
        gettext(
            '%(seat_label)s has been occupied with ticket %(ticket_code)s.',
            seat_label=seat.label,
            ticket_code=ticket.code,
        )
    )


@blueprint.delete('/ticket/<uuid:ticket_id>/seat')
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

    release_seat_result = ticket_seat_management_service.release_seat(
        ticket.id, manager
    )

    if release_seat_result.is_err():
        err = release_seat_result.unwrap_err()
        if isinstance(
            err, ticketing_errors.SeatChangeDeniedForBundledTicketError
        ):
            flash_error(
                gettext(
                    'Ticket %(ticket_code)s belongs to a bundle and cannot be managed separately.',
                    ticket_code=ticket.code,
                )
            )
        else:
            flash_error(gettext('An unexpected error occurred.'))

        return

    flash_success(
        gettext('%(seat_label)s has been released.', seat_label=seat.label)
    )


def _is_seat_management_enabled():
    if not g.user.authenticated:
        return False

    if not g.party:
        return False

    if _is_current_user_seating_admin():
        return True

    if not g.party.seat_management_enabled:
        return False

    return _user_manages_enough_tickets()


def _is_current_user_seating_admin() -> bool:
    return has_current_user_permission('ticketing.administrate_seat_occupancy')


def _user_manages_enough_tickets() -> bool:
    now_utc = datetime.utcnow()

    managed_tickets = ticket_service.get_tickets_for_seat_manager(
        g.user.id, g.party.id
    )
    managed_ticket_quantity = len(managed_tickets)

    return seat_reservation_service.is_reservation_allowed(
        g.party.id, now_utc, managed_ticket_quantity
    )


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
