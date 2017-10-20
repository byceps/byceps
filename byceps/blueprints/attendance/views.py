"""
byceps.blueprints.attendance.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
"""

from collections import namedtuple

from flask import g, request

from ...services.seating import seat_service
from ...services.ticketing import ticket_service
from ...services.user import service as user_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.templating import templated


blueprint = create_blueprint('attendance', __name__)


Attendee = namedtuple('Attendee', ['user', 'seat'])


@blueprint.route('/attendees', defaults={'page': 1})
@blueprint.route('/attendees/pages/<int:page>')
@templated
def attendees(page):
    """List all attendees of the current party."""
    per_page = request.args.get('per_page', type=int, default=30)
    search_term = request.args.get('search_term', default='').strip()

    pagination = ticket_service.get_tickets_in_use_for_party_paginated(
        g.party_id, page, per_page, search_term=search_term)

    tickets = pagination.items

    user_ids = {t.used_by_id for t in tickets}
    users = user_service.find_users(user_ids)
    users_by_id = user_service.index_users_by_id(users)

    seat_ids = {t.occupied_seat_id for t in tickets}
    seats = seat_service.find_seats(seat_ids)
    seats_by_id = {seat.id: seat for seat in seats}

    attendees = [
        Attendee(
            users_by_id[t.used_by_id],
            seats_by_id.get(t.occupied_seat_id),
        )
        for t in tickets
    ]

    pagination.items = attendees

    return {
        'search_term': search_term,
        'attendees': pagination,
    }
