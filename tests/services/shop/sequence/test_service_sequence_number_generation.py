"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.sequence.service import (
    generate_article_number,
    generate_order_number,
)

from tests.helpers import create_brand, create_email_config, create_party
from tests.services.shop.base import ShopTestBase


class SequenceNumberGenerationTestCase(ShopTestBase):

    def setUp(self):
        super().setUp()

        create_email_config()

        self.shop = self.create_shop()

        brand = create_brand()
        self.party = create_party(brand.id)

    def test_generate_article_number_default(self):
        self.create_article_number_sequence(self.shop.id, 'AEC-01-A')

        actual = generate_article_number(self.shop.id)

        assert actual == 'AEC-01-A00001'

    def test_generate_article_number_custom(self):
        last_assigned_article_sequence_number = 41

        self.create_article_number_sequence(self.shop.id, 'XYZ-09-A',
            value=last_assigned_article_sequence_number)

        actual = generate_article_number(self.shop.id)

        assert actual == 'XYZ-09-A00042'

    def test_generate_order_number_default(self):
        self.create_order_number_sequence(self.shop.id, 'AEC-01-B')

        actual = generate_order_number(self.shop.id)

        assert actual == 'AEC-01-B00001'

    def test_generate_order_number_custom(self):
        last_assigned_order_sequence_number = 206

        self.create_order_number_sequence(self.shop.id, 'LOL-03-B',
            value=last_assigned_order_sequence_number)

        actual = generate_order_number(self.shop.id)

        assert actual == 'LOL-03-B00207'
