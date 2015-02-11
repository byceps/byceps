# -*- coding: utf-8 -*-

from byceps.blueprints.shop.models import OrderNumberSequence
from byceps.blueprints.shop.service import generate_order_number

from testfixtures.brand import create_brand
from testfixtures.party import create_party

from tests import AbstractAppTestCase


class OrderNumberGenerationTestCase(AbstractAppTestCase):

    def test_generate_order_number_default(self):
        self.set_order_number_sequence()

        actual = generate_order_number(self.party)

        self.assertEqual(actual, 'AEC-01-B00001')

    def test_generate_order_number_custom(self):
        last_assigned_brand_order_serial = 206

        brand = create_brand(code='LOL')
        party = create_party(brand=brand, brand_party_serial=3)
        self.set_order_number_sequence(value=last_assigned_brand_order_serial)

        actual = generate_order_number(party)

        self.assertEqual(actual, 'LOL-03-B00207')

    def set_order_number_sequence(self, *, brand=None, value=0):
        if not brand:
            brand = self.brand

        sequence = OrderNumberSequence(brand=brand, value=value)
        self.db.session.add(sequence)
        self.db.session.commit()
