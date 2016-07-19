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
