"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.email import service as email_service
from byceps.services.shop.sequence.service import generate_article_number, \
    generate_order_number

from tests.helpers import create_brand, create_party
from tests.services.shop.base import ShopTestBase


class SequenceNumberGenerationTestCase(ShopTestBase):

    def setUp(self):
        super().setUp()

        brand = create_brand()
        self.party = create_party(brand_id=brand.id)

        self.email_config_id = brand.id
        email_service.set_sender(self.email_config_id, 'shop@example.com')

    def test_generate_article_number_default(self):
        shop = self.create_shop(self.party.id, self.email_config_id)
        self.create_article_number_sequence(shop.id, 'AEC-01-A')

        actual = generate_article_number(shop.id)

        assert actual == 'AEC-01-A00001'

    def test_generate_article_number_custom(self):
        shop = self.create_shop(self.party.id, self.email_config_id)
        last_assigned_article_sequence_number = 41

        self.create_article_number_sequence(shop.id, 'XYZ-09-A',
            value=last_assigned_article_sequence_number)

        actual = generate_article_number(shop.id)

        assert actual == 'XYZ-09-A00042'

    def test_generate_order_number_default(self):
        shop = self.create_shop(self.party.id, self.email_config_id)
        self.create_order_number_sequence(shop.id, 'AEC-01-B')

        actual = generate_order_number(shop.id)

        assert actual == 'AEC-01-B00001'

    def test_generate_order_number_custom(self):
        shop = self.create_shop(self.party.id, self.email_config_id)
        last_assigned_order_sequence_number = 206

        self.create_order_number_sequence(shop.id, 'LOL-03-B',
            value=last_assigned_order_sequence_number)

        actual = generate_order_number(shop.id)

        assert actual == 'LOL-03-B00207'
