"""
byceps.blueprints.admin.ticketing.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request

from ....services.party import service as party_service
from ....services.shop.order import service as order_service
from ....services.ticketing import (
    exceptions as ticket_exceptions,
    ticket_bundle_service,
    ticket_service,
    ticket_user_checkin_service,
    ticket_user_management_service,
)
from ....signals import ticketing as ticketing_signals
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_notice, flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, respond_no_content

from ...common.authorization.registry import permission_registry

from .authorization import TicketingPermission
from .forms import SpecifyUserForm
from . import service


blueprint = create_blueprint('ticketing_admin', __name__)


permission_registry.register_enum(TicketingPermission)


# -------------------------------------------------------------------- #
# tickets


@blueprint.route('/tickets/for_party/<party_id>', defaults={'page': 1})
@blueprint.route('/tickets/for_party/<party_id>/pages/<int:page>')
@permission_required(TicketingPermission.view)
@templated
def index_for_party(party_id, page):
    """List tickets for that party."""
    party = _get_party_or_404(party_id)

    per_page = request.args.get('per_page', type=int, default=15)

    search_term = request.args.get('search_term', default='').strip()

    tickets = ticket_service.get_tickets_with_details_for_party_paginated(
        party.id, page, per_page, search_term=search_term
    )

    return {
        'party': party,
        'search_term': search_term,
        'tickets': tickets,
    }


@blueprint.route('/tickets/<uuid:ticket_id>')
@permission_required(TicketingPermission.view)
@templated
def view_ticket(ticket_id):
    """Show a ticket."""
    ticket = ticket_service.get_ticket_with_details(ticket_id)
    if ticket is None:
        abort(404)

    party = party_service.get_party(ticket.category.party_id)

    if ticket.order_number:
        order = order_service.find_order_by_order_number(ticket.order_number)
    else:
        order = None

    events = service.get_events(ticket.id)

    return {
        'party': party,
        'ticket': ticket,
        'order': order,
        'events': events,
    }


# -------------------------------------------------------------------- #
# user appointment


@blueprint.route('/tickets/<uuid:ticket_id>/appoint_user')
@permission_required(TicketingPermission.checkin)
@templated
def appoint_user_form(ticket_id, erroneous_form=None):
    """Show a form to select a user to appoint for the ticket."""
    ticket = _get_ticket_or_404(ticket_id)

    party = party_service.get_party(ticket.category.party_id)

    form = erroneous_form if erroneous_form else SpecifyUserForm()

    return {
        'party': party,
        'ticket': ticket,
        'form': form,
    }


@blueprint.route('/tickets/<uuid:ticket_id>/user', methods=['POST'])
@permission_required(TicketingPermission.checkin)
def appoint_user(ticket_id):
    """Appoint a user for the ticket."""
    form = SpecifyUserForm(request.form)
    if not form.validate():
        return appoint_user_form(ticket_id, form)

    ticket = _get_ticket_or_404(ticket_id)
    user = form.user.data
    manager = g.current_user

    ticket_user_management_service.appoint_user(ticket.id, user.id, manager.id)

    flash_success(
        f'{user.screen_name} wurde als Nutzer/in '
        f'von Ticket {ticket.code} eingetragen.'
    )

    return redirect_to('.view_ticket', ticket_id=ticket.id)


# -------------------------------------------------------------------- #
# checked-in flag


@blueprint.route(
    '/tickets/<uuid:ticket_id>/flags/user_checked_in', methods=['POST']
)
@permission_required(TicketingPermission.checkin)
@respond_no_content
def set_user_checked_in_flag(ticket_id):
    """Check the user in."""
    ticket = _get_ticket_or_404(ticket_id)

    initiator_id = g.current_user.id

    try:
        event = ticket_user_checkin_service.check_in_user(
            ticket.id, initiator_id
        )
    except ticket_exceptions.UserAccountDeleted:
        flash_error(
            'Das dem Ticket zugewiesene Benutzerkonto ist gelöscht worden. '
            'Der Check-In ist nicht erlaubt.'
        )
        return
    except ticket_exceptions.UserAccountSuspended:
        flash_error(
            'Das dem Ticket zugewiesene Benutzerkonto ist gesperrt. '
            'Der Check-In ist nicht erlaubt.'
        )
        return

    ticketing_signals.ticket_checked_in.send(None, event=event)

    flash_success(f"Benutzer '{ticket.used_by.screen_name}' wurde eingecheckt.")

    occupies_seat = ticket.occupied_seat_id is not None
    if not occupies_seat:
        flash_notice('Das Ticket belegt noch keinen Sitzplatz.', icon='warning')


@blueprint.route(
    '/tickets/<uuid:ticket_id>/flags/user_checked_in', methods=['DELETE']
)
@permission_required(TicketingPermission.checkin)
@respond_no_content
def unset_user_checked_in_flag(ticket_id):
    """Revert the user check-in state."""
    ticket = _get_ticket_or_404(ticket_id)

    initiator_id = g.current_user.id

    ticket_user_checkin_service.revert_user_check_in(ticket.id, initiator_id)

    flash_success('Der Check-In wurde rückgängig gemacht.')


# -------------------------------------------------------------------- #
# bundles


@blueprint.route('/bundles/for_party/<party_id>', defaults={'page': 1})
@blueprint.route('/bundles/for_party/<party_id>/pages/<int:page>')
@permission_required(TicketingPermission.view)
@templated
def index_bundle_for_party(party_id, page):
    """List ticket bundles for that party."""
    party = _get_party_or_404(party_id)

    per_page = request.args.get('per_page', type=int, default=15)

    bundles = ticket_bundle_service.get_bundles_for_party_paginated(
        party.id, page, per_page
    )

    return {
        'party': party,
        'bundles': bundles,
    }


@blueprint.route('/bundles/<uuid:bundle_id>')
@permission_required(TicketingPermission.view)
@templated
def view_bundle(bundle_id):
    """Show a ticket bundle."""
    bundle = ticket_bundle_service.find_bundle(bundle_id)
    if bundle is None:
        abort(404)

    party = party_service.get_party(bundle.ticket_category.party_id)

    tickets = ticket_bundle_service.find_tickets_for_bundle(bundle.id)

    return {
        'party': party,
        'bundle': bundle,
        'tickets': tickets,
    }


# -------------------------------------------------------------------- #
# helpers


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_ticket_or_404(ticket_id):
    ticket = ticket_service.find_ticket(ticket_id)

    if ticket is None:
        abort(404)

    return ticket
