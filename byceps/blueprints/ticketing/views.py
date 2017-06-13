"""
byceps.blueprints.ticketing.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ...services.ticketing import ticket_service
from ...util.framework.blueprint import create_blueprint
from ...util.iterables import find
from ...util.templating import templated


blueprint = create_blueprint('ticketing', __name__)


@blueprint.route('/mine')
@templated
def index_mine():
    """List tickets related to the current user."""
    me = get_current_user_or_403()

    tickets = ticket_service.find_tickets_related_to_user_for_party(
        me.id, g.party.id)

    current_user_uses_any_ticket = find(lambda t: t.used_by_id == me.id, tickets)

    return {
        'tickets': tickets,
        'current_user_uses_any_ticket': current_user_uses_any_ticket,
    }


def get_current_user_or_403():
    user = g.current_user
    if not user.is_active:
        abort(403)

    return user
