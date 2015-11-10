# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..party.models import Party
from ..seating.models import Category as SeatCategory
from ..ticket.models import Ticket


def get_parties_with_ticket_counts():
    """Yield (party, ticket count) pairs."""
    parties = Party.query.all()

    ticket_counts_by_party_id = _get_ticket_counts_by_party_id()

    for party in parties:
        ticket_count = ticket_counts_by_party_id.get(party.id, 0)
        yield party, ticket_count


def _get_ticket_counts_by_party_id():
    return dict(db.session \
        .query(
            SeatCategory.party_id,
            db.func.count(Ticket.id)
        ) \
        .join(Ticket) \
        .group_by(SeatCategory.party_id) \
        .all())
