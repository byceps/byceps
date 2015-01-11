# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party.models import Party
from ..ticket.models import Ticket

from .authorization import TicketPermission


blueprint = create_blueprint('ticket_admin', __name__)


permission_registry.register_enum(TicketPermission)


@blueprint.route('/')
@permission_required(TicketPermission.list)
@templated
def index():
    """List parties to choose from."""
    parties = Party.query.all()

    return {'parties': parties}


@blueprint.route('/<party_id>')
@permission_required(TicketPermission.list)
@templated
def index_for_party(party_id):
    """List tickets for that party."""
    party = Party.query.get_or_404(party_id)

    tickets = Ticket.query.for_party(party).order_by(Ticket.created_at).all()

    return {
        'party': party,
        'tickets': tickets,
    }
