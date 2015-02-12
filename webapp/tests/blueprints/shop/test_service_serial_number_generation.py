# -*- coding: utf-8 -*-

from byceps.blueprints.shop.models import PartySequencePurpose
from byceps.blueprints.shop.service import generate_order_number

from testfixtures.brand import create_brand
from testfixtures.party import create_party
from testfixtures.shop import create_party_sequence

from tests import AbstractAppTestCase


class SerialNumberGenerationTestCase(AbstractAppTestCase):

    def test_generate_order_number_default(self):
        self.set_order_number_sequence()

        actual = generate_order_number(self.party)

        self.assertEqual(actual, 'AEC-01-B00001')

    def test_generate_order_number_custom(self):
        last_assigned_order_serial_number = 206

        brand = create_brand(code='LOL')
        party = create_party(brand=brand, brand_party_serial=3)
        self.set_order_number_sequence(value=last_assigned_order_serial_number)

        actual = generate_order_number(party)

        self.assertEqual(actual, 'LOL-03-B00207')

    def set_order_number_sequence(self, *, party=None, value=0):
        if not party:
            party = self.party

        sequence = create_party_sequence(party,
                                         PartySequencePurpose.order,
                                         value=value)
        self.db.session.add(sequence)
        self.db.session.commit()
