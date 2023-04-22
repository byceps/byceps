"""
byceps.blueprints.admin.ticketing.checkin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from datetime import date

from flask import abort, g, request, url_for
from flask_babel import gettext

from byceps.services.party import party_service
from byceps.services.party.models import Party
from byceps.services.shop.order import order_service
from byceps.services.shop.order.models.order import AdminOrderListItem
from byceps.services.shop.shop import shop_service
from byceps.services.ticketing import (
    exceptions as ticket_exceptions,
    ticket_service,
    ticket_user_checkin_service,
)
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import TicketID
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.signals import ticketing as ticketing_signals
from byceps.typing import BrandID, PartyID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_notice, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, respond_no_content


blueprint = create_blueprint('ticketing_checkin_admin', __name__)


MINIMUM_AGE_IN_YEARS = 18


@blueprint.get('/for_party/<party_id>')
@permission_required('ticketing.checkin')
@templated
def index(party_id):
    """Provide form to find tickets, then check them in."""
    party = _get_party_or_404(party_id)

    search_term = request.args.get('search_term', default='').strip()

    limit = 10

    if search_term:
        latest_dob_for_checkin = _get_latest_date_of_birth_for_checkin()
        tickets = _search_tickets(party.id, search_term, limit)
        orders = _search_orders(party.brand_id, search_term, limit)
        users = _search_users(search_term, limit)

        tickets += list(_get_tickets_for_users(party.id, users))
    else:
        latest_dob_for_checkin = None
        tickets = None
        orders = None
        users = None

    return {
        'party': party,
        'latest_dob_for_checkin': latest_dob_for_checkin,
        'search_term': search_term,
        'tickets': tickets,
        'orders': orders,
        'users': users,
    }


def _get_latest_date_of_birth_for_checkin() -> date:
    today = date.today()
    return today.replace(year=today.year - MINIMUM_AGE_IN_YEARS)


def _search_tickets(
    party_id: PartyID, search_term: str, limit: int
) -> list[DbTicket]:
    page = 1
    per_page = limit

    tickets_pagination = (
        ticket_service.get_tickets_with_details_for_party_paginated(
            party_id, page, per_page, search_term=search_term
        )
    )

    return tickets_pagination.items


def _search_orders(
    brand_id: BrandID, search_term: str, limit: int
) -> list[AdminOrderListItem]:
    shop = shop_service.find_shop_for_brand(brand_id)
    if shop is None:
        return []

    page = 1
    per_page = limit

    orders_pagination = order_service.get_orders_for_shop_paginated(
        shop.id, page, per_page, search_term=search_term
    )

    return orders_pagination.items


def _search_users(search_term: str, limit: int) -> list[User]:
    page = 1
    per_page = limit

    users_pagination = user_service.get_users_paginated(
        page, per_page, search_term=search_term
    )

    # Exclude deleted users.
    users_pagination.items = [
        user for user in users_pagination.items if not user.deleted
    ]

    return users_pagination.items


def _get_tickets_for_users(
    party_id: PartyID, users: list[User]
) -> Iterator[DbTicket]:
    for user in users:
        yield from ticket_service.get_tickets_related_to_user_for_party(
            user.id, party_id
        )


@blueprint.post('/for_party/<party_id>/tickets/<uuid:ticket_id>/check_in_user')
@permission_required('ticketing.checkin')
@respond_no_content
def check_in_user(party_id, ticket_id):
    """Check the user in."""
    party = _get_party_or_404(party_id)
    ticket = _get_ticket_or_404(ticket_id)

    initiator_id = g.user.id

    try:
        event = ticket_user_checkin_service.check_in_user(
            party.id, ticket.id, initiator_id
        )
    except ticket_exceptions.UserAccountDeleted:
        flash_error(
            gettext(
                'The user account assigned to this ticket has been deleted. Check-in denied.'
            )
        )
        return
    except ticket_exceptions.UserAccountSuspended:
        flash_error(
            gettext(
                'The user account assigned to this ticket has been suspended. Check-in denied.'
            )
        )
        return

    ticketing_signals.ticket_checked_in.send(None, event=event)

    ticket_url = url_for('ticketing_admin.view_ticket', ticket_id=ticket.id)

    flash_success(
        gettext(
            'User <em>%(screen_name)s</em> has been checked in with ticket <a href="%(ticket_url)s">%(ticket_code)s</a>.',
            screen_name=ticket.used_by.screen_name,
            ticket_url=ticket_url,
            ticket_code=ticket.code,
        ),
        text_is_safe=True,
    )

    occupies_seat = ticket.occupied_seat_id is not None
    if not occupies_seat:
        flash_notice(
            gettext(
                'Ticket <a href="%(ticket_url)s">%(ticket_code)s</a> does not occupy a seat.',
                ticket_url=ticket_url,
                ticket_code=ticket.code,
            ),
            icon='warning',
            text_is_safe=True,
        )


@blueprint.post('/tickets/<uuid:ticket_id>/revert_user_check_in')
@permission_required('ticketing.checkin')
@respond_no_content
def revert_user_check_in(ticket_id):
    """Revert the user check-in state."""
    ticket = _get_ticket_or_404(ticket_id)

    initiator_id = g.user.id

    ticket_user_checkin_service.revert_user_check_in(ticket.id, initiator_id)

    flash_success(gettext('Check-in has been reverted.'))


def _get_party_or_404(party_id: PartyID) -> Party:
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_ticket_or_404(ticket_id: TicketID) -> DbTicket:
    ticket = ticket_service.find_ticket(ticket_id)

    if ticket is None:
        abort(404)

    return ticket
