"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.sequence import service as sequence_service

from tests.helpers import create_email_config
from tests.services.shop.base import ShopTestBase


class SequenceNumberGenerationTestCase(ShopTestBase):

    def setUp(self):
        super().setUp()

        create_email_config()

        self.shop = self.create_shop()

    def test_generate_article_number_default(self):
        sequence_service.create_article_number_sequence(self.shop.id, 'AEC-01-A')

        actual = sequence_service.generate_article_number(self.shop.id)

        assert actual == 'AEC-01-A00001'

    def test_generate_article_number_custom(self):
        sequence_service.create_article_number_sequence(
            self.shop.id,
            'XYZ-09-A',
            value=41,
        )

        actual = sequence_service.generate_article_number(self.shop.id)

        assert actual == 'XYZ-09-A00042'

    def test_generate_order_number_default(self):
        self.create_order_number_sequence(self.shop.id, 'AEC-01-B')

        actual = sequence_service.generate_order_number(self.shop.id)

        assert actual == 'AEC-01-B00001'

    def test_generate_order_number_custom(self):
        last_assigned_order_sequence_number = 206

        self.create_order_number_sequence(
            self.shop.id, 'LOL-03-B', value=last_assigned_order_sequence_number
        )

        actual = sequence_service.generate_order_number(self.shop.id)

        assert actual == 'LOL-03-B00207'
