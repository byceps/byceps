# -*- coding: utf-8 -*-

"""
byceps.services.shop.sequence.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db

from .models import PartySequence, PartySequencePurpose


def generate_article_number(party):
    """Generate and reserve an unused, unique article number for this party."""
    prefix = party.shop_number_prefix.article_number

    article_sequence_number = _get_next_sequence_number(party.id,
        PartySequencePurpose.article)

    return '{}{:05d}'.format(prefix, article_sequence_number)


def generate_order_number(party):
    """Generate and reserve an unused, unique order number for this party."""
    prefix = party.shop_number_prefix.order_number

    order_sequence_number = _get_next_sequence_number(party.id,
        PartySequencePurpose.order)

    return '{}{:05d}'.format(prefix, order_sequence_number)


def _get_next_sequence_number(party_id, purpose):
    """Calculate and reserve the next sequence number for the party and
    purpose.
    """
    sequence = PartySequence.query \
        .filter_by(party_id=party_id) \
        .filter_by(_purpose=purpose.name) \
        .with_for_update() \
        .one_or_none()

    if sequence is None:
        sequence = PartySequence(party.id, purpose)
        db.session.add(sequence)
        db.session.commit()

    sequence.value = PartySequence.value + 1
    db.session.commit()
    return sequence.value


def get_article_number_prefix(party):
    """Return the article number prefix for that party, or `None` if
    none is defined.
    """
    return getattr(party.shop_number_prefix, 'article_number', None)


def get_order_number_prefix(party):
    """Return the order number prefix for that party, or `None` if
    none is defined.
    """
    return getattr(party.shop_number_prefix, 'order_number', None)
