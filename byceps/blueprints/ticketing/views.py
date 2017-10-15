"""
byceps.blueprints.ticketing.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ...services.party import service as party_service
from ...services.ticketing import ticket_service
from ...util.framework.blueprint import create_blueprint
from ...util.iterables import find
from ...util.framework.templating import templated


blueprint = create_blueprint('ticketing', __name__)


@blueprint.route('/mine')
@templated
def index_mine():
    """List tickets related to the current user."""
    current_user = _get_current_user_or_403()

    party = party_service.find_party(g.party_id)

    tickets = ticket_service.find_tickets_related_to_user_for_party(
        current_user.id, party.id)

    tickets = [ticket for ticket in tickets if not ticket.revoked]

    current_user_uses_any_ticket = find(
        lambda t: t.used_by_id == current_user.id, tickets)

    return {
        'party_title': party.title,
        'tickets': tickets,
        'current_user_uses_any_ticket': current_user_uses_any_ticket,
    }


def _get_current_user_or_403():
    user = g.current_user

    if not user.is_active:
        abort(403)

    return user
