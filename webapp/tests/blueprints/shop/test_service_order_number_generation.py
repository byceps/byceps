# -*- coding: utf-8 -*-

from unittest import TestCase

from byceps.blueprints.shop.service import generate_order_number

from testfixtures.party import create_party


class OrderNumberGenerationTestCase(TestCase):

    def test_generate_order_number(self):
        brand_order_serial = 207

        party = create_party(brand_party_serial=3)

        def generate_brand_order_serial(brand):
            return brand_order_serial

        actual = generate_order_number(party,
            brand_order_serial_generator=generate_brand_order_serial)

        self.assertEqual(actual, 'AEC-03-B00207')
