"""
testfixtures.seating
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.seating.models.seat_group import SeatGroup


def create_seat_group(party_id, ticket_category_id, title, *, seat_quantity=4):
    return SeatGroup(party_id, ticket_category_id, seat_quantity, title)
