"""
testfixtures.seating
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.seating.models.category import Category
from byceps.services.seating.models.seat_group import SeatGroup


def create_seat_category(party_id, title):
    return Category(party_id, title)


def create_seat_group(party_id, seat_category_id, title, *, seat_quantity=4):
    return SeatGroup(party_id, seat_category_id, seat_quantity, title)
