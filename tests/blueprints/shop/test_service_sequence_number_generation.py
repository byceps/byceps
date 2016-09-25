# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.sequence.service import generate_article_number, \
    generate_order_number
from byceps.services.shop.sequence.models import PartySequencePurpose

from testfixtures.brand import create_brand
from testfixtures.party import create_party
from testfixtures.shop import create_party_sequence, \
    create_party_sequence_prefix

from tests.base import AbstractAppTestCase


class SequenceNumberGenerationTestCase(AbstractAppTestCase):

    def test_generate_article_number_default(self):
        self.setup_article_number_sequence(self.party, 'AEC-01-A')

        actual = generate_article_number(self.party)

        self.assertEqual(actual, 'AEC-01-A00001')

    def test_generate_article_number_custom(self):
        party = self.create_custom_brand_and_party()
        last_assigned_article_sequence_number = 41

        self.setup_article_number_sequence(party, 'XYZ-09-A',
            value=last_assigned_article_sequence_number)

        actual = generate_article_number(party)

        self.assertEqual(actual, 'XYZ-09-A00042')

    def test_generate_order_number_default(self):
        self.setup_order_number_sequence(self.party, 'AEC-01-B')

        actual = generate_order_number(self.party)

        self.assertEqual(actual, 'AEC-01-B00001')

    def test_generate_order_number_custom(self):
        party = self.create_custom_brand_and_party()
        last_assigned_order_sequence_number = 206

        self.setup_order_number_sequence(party, 'LOL-03-B',
            value=last_assigned_order_sequence_number)

        actual = generate_order_number(party)

        self.assertEqual(actual, 'LOL-03-B00207')

    # -------------------------------------------------------------------- #
    # helpers

    def create_custom_brand_and_party(self):
        brand = create_brand(id='custom', title='Custom Events')
        party = create_party(id='custom-party-4', brand=brand,
                             title='Custom Party 4')

        self._persist(brand, party)

        return party

    def setup_article_number_sequence(self, party, prefix, *, value=0):
        sequence_prefix = create_party_sequence_prefix(party,
            article_number_prefix=prefix)

        purpose = PartySequencePurpose.article
        sequence = create_party_sequence(party, purpose, value=value)

        self._persist(sequence_prefix, sequence)

    def setup_order_number_sequence(self, party, prefix, *, value=0):
        sequence_prefix = create_party_sequence_prefix(party,
            order_number_prefix=prefix)

        purpose = PartySequencePurpose.order
        sequence = create_party_sequence(party, purpose, value=value)

        self._persist(sequence_prefix, sequence)

    def _persist(self, *instances):
        self.db.session.add_all(instances)
        self.db.session.commit()
