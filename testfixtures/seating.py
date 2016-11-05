# -*- coding: utf-8 -*-

"""
testfixtures.seating
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.seating.models.seat_group import SeatGroup


def create_seat_group(party_id, seat_category, title, *, seat_quantity=4):
    return SeatGroup(party_id, seat_category, seat_quantity, title)
