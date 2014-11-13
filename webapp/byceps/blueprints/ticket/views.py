# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import abort, g

from ...util.framework import create_blueprint
from ...util.templating import templated

from .models import Ticket


blueprint = create_blueprint('ticket', __name__)


@blueprint.route('/mine')
@templated
def index_mine():
    """List tickets related to the current user."""
    me = get_current_user_or_403()

    tickets = Ticket.query \
        .for_current_party() \
        .filter(
            (Ticket.owned_by == me) |
            (Ticket.seat_managed_by == me) |
            (Ticket.user_managed_by == me) |
            (Ticket.used_by == me)
        ) \
        .order_by(Ticket.created_at) \
        .all()

    tickets_bought = [ticket for ticket in tickets if ticket.owned_by == me]
    tickets_managed = [ticket for ticket in tickets if ticket.is_managed_by(me)]
    tickets_mine = [ticket for ticket in tickets if ticket.used_by == me]
    ticket_mine = tickets_mine[0] if len(tickets_mine) == 1 else None

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
