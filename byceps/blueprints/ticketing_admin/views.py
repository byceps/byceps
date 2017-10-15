"""
byceps.blueprints.ticketing_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ...services.party import service as party_service
from ...services.shop.order import service as order_service
from ...services.ticketing import ticket_bundle_service, ticket_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import TicketingPermission


blueprint = create_blueprint('ticketing_admin', __name__)


permission_registry.register_enum(TicketingPermission)


@blueprint.route('/tickets/for_party/<party_id>', defaults={'page': 1})
@blueprint.route('/tickets/for_party/<party_id>/pages/<int:page>')
@permission_required(TicketingPermission.view)
@templated
def index_for_party(party_id, page):
    """List tickets for that party."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    per_page = request.args.get('per_page', type=int, default=15)

    tickets = ticket_service.get_tickets_with_details_for_party_paginated(
        party.id, page, per_page)

    return {
        'party': party,
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

    party = party_service.find_party(ticket.category.party_id)

    if ticket.order_number:
        order = order_service.find_order_by_order_number(ticket.order_number)
    else:
        order = None

    return {
        'party': party,
        'ticket': ticket,
        'order': order,
    }


@blueprint.route('/bundles/<uuid:bundle_id>')
@permission_required(TicketingPermission.view)
@templated
def view_bundle(bundle_id):
    """Show a ticket bundle."""
    bundle = ticket_bundle_service.find_bundle(bundle_id)
    if bundle is None:
        abort(404)

    party = party_service.find_party(bundle.ticket_category.party_id)

    tickets = ticket_bundle_service.find_tickets_for_bundle(bundle.id)

    return {
        'party': party,
        'bundle': bundle,
        'tickets': tickets,
    }
