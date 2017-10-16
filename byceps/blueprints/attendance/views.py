"""
byceps.blueprints.attendance.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
"""

from flask import g, request

from ...services.ticketing import ticket_service
from ...services.user import service as user_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated


blueprint = create_blueprint('attendance', __name__)


@blueprint.route('/attendees', defaults={'page': 1})
@blueprint.route('/attendees/pages/<int:page>')
@templated
def attendees(page):
    """List all attendees of the current party."""
    per_page = request.args.get('per_page', type=int, default=50)
    search_term = request.args.get('search_term', default='').strip()

    tickets = ticket_service.get_tickets_in_use_for_party_paginated(
        g.party_id, page, per_page, search_term=search_term)

    user_ids = {t.used_by_id for t in tickets.items}
    users = user_service.find_users(user_ids)
    users_by_id = user_service.index_users_by_id(users)

    tickets.items = [
        {
            'user': users_by_id[t.used_by_id],
        }
        for t in tickets.items
    ]

    return {
        'search_term': search_term,
        'tickets': tickets,
    }
