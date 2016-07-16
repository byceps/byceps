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
