# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..seating.models.category import Category as SeatCategory
from ..ticket.models import Ticket


def get_ticket_counts_by_party_id():
    """Return ticket counts per party, indexed by party ID.

    Entries for parties without existing tickets are exluded.
    """
    return dict(db.session \
        .query(
            SeatCategory.party_id,
            db.func.count(Ticket.id)
        ) \
        .join(Ticket) \
        .group_by(SeatCategory.party_id) \
        .all())
