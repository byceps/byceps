# -*- coding: utf-8 -*-

"""
byceps.blueprints.party.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from ...database import db

from ..seating.models import Category as SeatCategory
from ..ticket.models import Ticket
from ..user.models import User

from .models import Party


def get_archived_parties():
    """Return archived parties."""
    return Party.query \
        .filter_by(is_archived=True) \
        .order_by(Party.starts_at.desc()) \
        .all()


def get_attendee_screen_names_by_party(parties):
    """Return the screen names of the parties' attendees, grouped by party."""
    return {party: get_attendee_screen_names(party) for party in parties}


def get_attendee_screen_names(party):
    """Return the screen names of the party's attendees."""
    users = User.query \
        .options(db.load_only('screen_name')) \
        .join(Ticket.used_by) \
        .join(SeatCategory).filter(SeatCategory.party == party) \
        .all()

    return frozenset(map(attrgetter('screen_name'), users))
