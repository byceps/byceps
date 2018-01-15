"""
testfixtures.shop_sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.sequence.models import PartySequence


def create_party_sequence(party_id, purpose, prefix, *, value=0):
    sequence = PartySequence(party_id, purpose, prefix)
    sequence.value = value
    return sequence
