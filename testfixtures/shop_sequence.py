"""
testfixtures.shop_sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.sequence.models import NumberSequence


def create_sequence(shop_id, purpose, prefix, *, value=0):
    sequence = NumberSequence(shop_id, purpose, prefix)
    sequence.value = value
    return sequence
