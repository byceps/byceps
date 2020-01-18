"""
testfixtures.ticketing
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.ticketing.models.category import Category


def create_ticket_category(party_id, title):
    return Category(party_id, title)
