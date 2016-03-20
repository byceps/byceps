# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..party.models import Party
from ..seating.models.category import Category
from ..seating.models.seat import Seat

from .models import Ticket


def find_tickets_used_by_user(user, party):
    """Return the tickets (if any) used by the user for that party."""
    if user.is_anonymous:
        return []

    return Ticket.query \
        .for_party(party) \
        .filter(Ticket.used_by == user) \
        .join(Seat) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .order_by(Seat.coord_x, Seat.coord_y) \
        .all()


def uses_any_ticket_for_party(user, party):
    """Return `True` if the user uses any ticket for that party."""
    if user.is_anonymous:
        return False

    count = Ticket.query \
        .for_party(party) \
        .filter(Ticket.used_by == user) \
        .count()

    return count > 0


def get_attended_parties(user):
    """Return the parties the user has attended."""
    return Party.query \
        .join(Category).join(Ticket).filter(Ticket.used_by == user) \
        .all()


def count_tickets_for_party(party):
    """Return the number of "sold" (i.e. generated) tickets for that party."""
    return Ticket.query.for_party(party).count()
