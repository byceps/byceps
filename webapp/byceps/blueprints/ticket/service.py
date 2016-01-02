# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..party.models import Party
from ..seating.models import Category

from .models import Ticket


def find_ticket_for_user(user, party):
    """Return the ticket used by the user for the party, or `None` if not
    found.
    """
    if user.is_anonymous:
        return None

    return Ticket.query \
        .filter(Ticket.used_by == user) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .for_party(party) \
        .first()


def get_attended_parties(user):
    """Return the parties the user has attended."""
    return Party.query \
        .join(Category).join(Ticket).filter(Ticket.used_by == user) \
        .all()


def count_tickets_for_party(party):
    """Return the number of "sold" (i.e. generated) tickets for that party."""
    return Ticket.query \
        .join(Category).filter(Category.party_id == party.id) \
        .count()
