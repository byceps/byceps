# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g

from ...services.ticket import service as ticket_service
from ...util.framework import create_blueprint
from ...util.iterables import find
from ...util.templating import templated


blueprint = create_blueprint('ticket', __name__)


@blueprint.route('/mine')
@templated
def index_mine():
    """List tickets related to the current user."""
    me = get_current_user_or_403()

    tickets = ticket_service.find_tickets_related_to_user_for_party(me, g.party)

    tickets_bought = list(filter(lambda t: t.owned_by == me, tickets))
    tickets_managed = list(filter(lambda t: t.is_managed_by(me), tickets))
    ticket_mine = find(lambda t: t.used_by == me, tickets)

    return {
        'tickets_bought': tickets_bought,
        'tickets_managed': tickets_managed,
        'ticket_mine': ticket_mine,
    }


def get_current_user_or_403():
    user = g.current_user
    if not user.is_active:
        abort(403)

    return user
