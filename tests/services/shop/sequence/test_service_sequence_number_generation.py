"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.sequence.service import generate_article_number, \
    generate_order_number
from byceps.services.shop.sequence.transfer.models import Purpose

from testfixtures.shop_sequence import create_sequence
from testfixtures.shop_shop import create_shop

from tests.base import AbstractAppTestCase


class SequenceNumberGenerationTestCase(AbstractAppTestCase):

    def test_generate_article_number_default(self):
        self.create_brand_and_party()
        shop = self.setup_shop(self.party.id)
        self.setup_article_number_sequence(shop.id, 'AEC-01-A')

        actual = generate_article_number(shop.id)

        assert actual == 'AEC-01-A00001'

    def test_generate_article_number_custom(self):
        party = self.create_custom_brand_and_party()
        shop = self.setup_shop(party.id)
        last_assigned_article_sequence_number = 41

        self.setup_article_number_sequence(shop.id, 'XYZ-09-A',
            value=last_assigned_article_sequence_number)

        actual = generate_article_number(shop.id)

        assert actual == 'XYZ-09-A00042'

    def test_generate_order_number_default(self):
        self.create_brand_and_party()
        shop = self.setup_shop(self.party.id)
        self.setup_order_number_sequence(shop.id, 'AEC-01-B')

        actual = generate_order_number(shop.id)

        assert actual == 'AEC-01-B00001'

    def test_generate_order_number_custom(self):
        party = self.create_custom_brand_and_party()
        shop = self.setup_shop(party.id)
        last_assigned_order_sequence_number = 206

        self.setup_order_number_sequence(shop.id, 'LOL-03-B',
            value=last_assigned_order_sequence_number)

        actual = generate_order_number(shop.id)

        assert actual == 'LOL-03-B00207'

    # -------------------------------------------------------------------- #
    # helpers

    def create_custom_brand_and_party(self):
        brand = self.create_brand('custom', 'Custom Events')
        party = self.create_party(brand.id, 'custom-party-4', 'Custom Party 4')

        return party

    def setup_shop(self, party_id):
        shop = create_shop(party_id)

        self.db.session.add(shop)
        self.db.session.commit()

        return shop

    def setup_article_number_sequence(self, shop_id, prefix, *, value=0):
        self._create_sequence(shop_id, Purpose.article, prefix, value)

    def setup_order_number_sequence(self, shop_id, prefix, *, value=0):
        self._create_sequence(shop_id, Purpose.order, prefix, value)

    def _create_sequence(self, shop_id, purpose, prefix, value):
        sequence = create_sequence(shop_id, purpose, prefix, value=value)

        self.db.session.add(sequence)
        self.db.session.commit()
