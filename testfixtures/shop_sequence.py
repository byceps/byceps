"""
testfixtures.shop_sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.sequence.models import Sequence


def create_sequence(party_id, purpose, prefix, *, value=0):
    sequence = Sequence(party_id, purpose, prefix)
    sequence.value = value
    return sequence
