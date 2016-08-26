# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, request

from ...database import db
from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party import service as party_service

from .authorization import TicketPermission
from . import service


blueprint = create_blueprint('ticket_admin', __name__)


permission_registry.register_enum(TicketPermission)


@blueprint.route('/for_party/<party_id>', defaults={'page': 1})
@blueprint.route('/for_party/<party_id>/pages/<int:page>')
@permission_required(TicketPermission.list)
@templated
def index_for_party(party_id, page):
    """List tickets for that party."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    per_page = request.args.get('per_page', type=int, default=15)

    tickets = service.get_tickets_with_details_for_party_paginated(party, page,
                                                                   per_page)

    return {
        'party': party,
        'tickets': tickets,
    }


@blueprint.route('/<uuid:id>')
@permission_required(TicketPermission.view)
@templated
def view(id):
    """Show a ticket."""
    ticket = service.get_ticket_with_details(id)
    if ticket is None:
        abort(404)

    return {
        'ticket': ticket,
    }
