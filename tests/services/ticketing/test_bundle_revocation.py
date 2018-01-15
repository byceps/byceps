"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.ticketing import category_service, event_service, \
    ticket_bundle_service as bundle_service

from tests.base import AbstractAppTestCase


class TicketBundleRevocationTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.quantity = 4

        bundle = self.create_bundle(self.quantity)

        self.bundle_id = bundle.id

    def test_revoke_bundle(self):
        tickets_before = bundle_service.find_tickets_for_bundle(self.bundle_id)
        assert len(tickets_before) == self.quantity

        for ticket_before in tickets_before:
            assert not ticket_before.revoked

            events_before = event_service.get_events_for_ticket(ticket_before.id)
            assert len(events_before) == 0

        # -------------------------------- #

        bundle_service.revoke_bundle(self.bundle_id)

        # -------------------------------- #

        tickets_after = bundle_service.find_tickets_for_bundle(self.bundle_id)
        assert len(tickets_after) == self.quantity

        for ticket_after in tickets_after:
            assert ticket_after.revoked

            events_after = event_service.get_events_for_ticket(ticket_after.id)
            assert len(events_after) == 1

            ticket_revoked_event = events_after[0]
            assert ticket_revoked_event.event_type == 'ticket-revoked'
            assert ticket_revoked_event.data == {}

    # -------------------------------------------------------------------- #
    # helpers

    def create_bundle(self, quantity):
        category = self.create_category('Premium')
        owner = self.create_user('Ticket_Owner')

        return bundle_service.create_bundle(category.id, quantity, owner.id)

    def create_category(self, title):
        return category_service.create_category(self.party.id, title)
