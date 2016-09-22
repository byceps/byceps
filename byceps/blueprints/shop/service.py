# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models.sequence import PartySequence, PartySequencePurpose


def generate_article_number(party):
    """Generate and reserve an unused, unique article number for this party."""
    prefix = party.shop_number_prefix.article_number

    article_serial_number = _get_next_serial_number(party,
                                                    PartySequencePurpose.article)

    return '{}{:05d}'.format(prefix, article_serial_number)


def generate_order_number(party):
    """Generate and reserve an unused, unique order number for this party."""
    prefix = party.shop_number_prefix.order_number

    order_serial_number = _get_next_serial_number(party,
                                                  PartySequencePurpose.order)

    return '{}{:05d}'.format(prefix, order_serial_number)


def _get_next_serial_number(party, purpose):
    """Calculate and reserve the next serial number for the party and purpose."""
    sequence = PartySequence.query \
        .filter_by(party=party) \
        .filter_by(_purpose=purpose.name) \
        .with_for_update() \
        .one_or_none()

    if sequence is None:
        sequence = PartySequence(party, purpose)
        db.session.add(sequence)
        db.session.commit()

    sequence.value = PartySequence.value + 1
    db.session.commit()
    return sequence.value
