# -*- coding: utf-8 -*-

"""
byceps.blueprints.party.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..seating.models.category import Category as SeatCategory
from ..ticket.models import Ticket
from ..user.models.user import User

from .models import Party


def count_parties():
    """Return the number of parties (of all brands)."""
    return Party.query.count()


def count_parties_for_brand(brand):
    """Return the number of parties for that brand."""
    return Party.query.for_brand(brand).count()


def find_party(party_id):
    """Return the party with that id, or `None` if not found."""
    return Party.query.get(party_id)


def find_party_with_brand(party_id):
    """Return the party with that id, or `None` if not found."""
    return Party.query \
        .options(db.joinedload('brand')) \
        .get(party_id)


def get_archived_parties():
    """Return archived parties."""
    return Party.query \
        .filter_by(is_archived=True) \
        .order_by(Party.starts_at.desc()) \
        .all()


def get_attendees_by_party(parties):
    """Return the parties' attendees, grouped by party."""
    return {party: get_attendees_for_party(party) for party in parties}


def get_attendees_for_party(party):
    """Return the party's attendees."""
    return User.query \
        .options(
            db.load_only('screen_name', 'deleted'),
            db.joinedload('avatar_selection').joinedload('avatar')
        ) \
        .join(Ticket.used_by) \
        .join(SeatCategory).filter(SeatCategory.party == party) \
        .all()
