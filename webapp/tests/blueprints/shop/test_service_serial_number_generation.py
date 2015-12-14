# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.shop.models.sequence import PartySequencePurpose
from byceps.blueprints.shop.service import generate_article_number, \
    generate_order_number

from testfixtures.brand import create_brand
from testfixtures.party import create_party
from testfixtures.shop import create_party_sequence, \
    create_party_sequence_prefix

from tests.base import AbstractAppTestCase


class SerialNumberGenerationTestCase(AbstractAppTestCase):

    def test_generate_article_number_default(self):
        create_party_sequence_prefix(self.party,
                                     article_number_prefix='AEC-01-A')
        self.set_article_number_sequence()

        actual = generate_article_number(self.party)

        self.assertEqual(actual, 'AEC-01-A00001')

    def test_generate_article_number_custom(self):
        last_assigned_article_serial_number = 41

        brand = create_brand()
        party = create_party(brand=brand)
        create_party_sequence_prefix(party, article_number_prefix='XYZ-09-A')
        self.set_article_number_sequence(value=last_assigned_article_serial_number)

        actual = generate_article_number(party)

        self.assertEqual(actual, 'XYZ-09-A00042')

    def test_generate_order_number_default(self):
        create_party_sequence_prefix(self.party, order_number_prefix='AEC-01-B')
        self.set_order_number_sequence()

        actual = generate_order_number(self.party)

        self.assertEqual(actual, 'AEC-01-B00001')

    def test_generate_order_number_custom(self):
        last_assigned_order_serial_number = 206

        brand = create_brand()
        party = create_party(brand=brand)
        create_party_sequence_prefix(party, order_number_prefix='LOL-03-B')
        self.set_order_number_sequence(value=last_assigned_order_serial_number)

        actual = generate_order_number(party)

        self.assertEqual(actual, 'LOL-03-B00207')

    # -------------------------------------------------------------------- #
    # helpers

    def set_article_number_sequence(self, *, party=None, value=0):
        self._set_number_sequence(PartySequencePurpose.article,
                                  party=party,
                                  value=value)

    def set_order_number_sequence(self, *, party=None, value=0):
        self._set_number_sequence(PartySequencePurpose.order,
                                  party=party,
                                  value=value)

    def _set_number_sequence(self, purpose, *, party=None, value=0):
        if not party:
            party = self.party

        sequence = create_party_sequence(party, purpose, value=value)
        self.db.session.add(sequence)
        self.db.session.commit()
