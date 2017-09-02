"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.seating import category_service
from byceps.services.ticketing import ticket_bundle_service as bundle_service

from tests.base import AbstractAppTestCase


class TicketBundleRevokeTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.quantity = 4

        bundle = self.create_bundle(self.quantity)

        self.bundle_id = bundle.id

    def test_revoke_bundle(self):
        tickets_before = bundle_service.find_tickets_for_bundle(self.bundle_id)
        self.assertLength(tickets_before, self.quantity)
        self.assertNotRevoked(tickets_before)

        bundle_service.revoke_bundle(self.bundle_id)

        tickets_after = bundle_service.find_tickets_for_bundle(self.bundle_id)
        self.assertLength(tickets_after, self.quantity)
        self.assertRevoked(tickets_after)

    # -------------------------------------------------------------------- #
    # helpers

    def create_bundle(self, quantity):
        category = self.create_category('Premium')
        owner = self.create_user('Ticket_Owner')

        return bundle_service.create_bundle(category.id, quantity, owner.id)

    def create_category(self, title):
        return category_service.create_category(self.party.id, title)

    def assertLength(self, collection, expected_length):
        self.assertEqual(len(collection), expected_length)

    def assertNotRevoked(self, tickets):
        for ticket in tickets:
            self.assertFalse(ticket.revoked)

    def assertRevoked(self, tickets):
        for ticket in tickets:
            self.assertTrue(ticket.revoked)
