# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..party.models import Party
from ..seating.models.category import Category as SeatCategory
from ..ticket.models import Ticket


def get_ticket_count_by_party_id():
    """Return ticket count (including 0) per party, indexed by party ID."""
    return dict(db.session \
        .query(
            Party.id,
            db.func.count(Ticket.id)
        ) \
        .outerjoin(SeatCategory) \
        .outerjoin(Ticket) \
        .group_by(Party.id) \
        .all())


def get_ticket_with_details(ticket_id):
    """Return the ticket with that id, or `None` if not found."""
    return Ticket.query \
        .options(
            db.joinedload('category'),
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('owned_by'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
        ) \
        .get(id)


def get_tickets_with_details_for_party_paginated(party, page, per_page):
    """Return the party's tickets to show on the specified page."""
    return Ticket.query \
        .for_party(party) \
        .options(
            db.joinedload('category'),
            db.joinedload('owned_by'),
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .order_by(Ticket.created_at) \
        .paginate(page, per_page)
