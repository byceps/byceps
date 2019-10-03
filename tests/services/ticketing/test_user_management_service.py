"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.ticketing import (
    category_service,
    event_service,
    ticket_creation_service,
    ticket_user_management_service,
)

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_party, create_user


class TicketUserManagementServiceTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.owner = create_user('Ticket_Owner')

        brand = create_brand()
        self.party = create_party(brand_id=brand.id)

        self.category_id = self.create_category('Premium').id

        self.ticket = ticket_creation_service \
            .create_ticket(self.category_id, self.owner.id)

    def test_appoint_and_withdraw_user_manager(self):
        manager = create_user('Ticket_Manager')

        assert self.ticket.user_managed_by_id is None

        # appoint user manager

        ticket_user_management_service \
            .appoint_user_manager(self.ticket.id, manager.id, self.owner.id)
        assert self.ticket.user_managed_by_id == manager.id

        events_after_appointment = event_service.get_events_for_ticket(
            self.ticket.id)
        assert len(events_after_appointment) == 1

        appointment_event = events_after_appointment[0]
        assert_event(appointment_event, 'user-manager-appointed', {
            'appointed_user_manager_id': str(manager.id),
            'initiator_id': str(self.owner.id),
        })

        # withdraw user manager

        ticket_user_management_service \
            .withdraw_user_manager(self.ticket.id, self.owner.id)
        assert self.ticket.user_managed_by_id is None

        events_after_withdrawal = event_service.get_events_for_ticket(
            self.ticket.id)
        assert len(events_after_withdrawal) == 2

        withdrawal_event = events_after_withdrawal[1]
        assert_event(withdrawal_event, 'user-manager-withdrawn', {
            'initiator_id': str(self.owner.id),
        })

    def test_appoint_and_withdraw_user(self):
        user = create_user('Ticket_User')

        assert self.ticket.used_by_id is None

        # appoint user

        ticket_user_management_service \
            .appoint_user(self.ticket.id, user.id, self.owner.id)
        assert self.ticket.used_by_id == user.id

        events_after_appointment = event_service.get_events_for_ticket(
            self.ticket.id)
        assert len(events_after_appointment) == 1

        appointment_event = events_after_appointment[0]
        assert_event(appointment_event, 'user-appointed', {
            'appointed_user_id': str(user.id),
            'initiator_id': str(self.owner.id),
        })

        # withdraw user

        ticket_user_management_service \
            .withdraw_user(self.ticket.id, self.owner.id)
        assert self.ticket.used_by_id is None

        events_after_withdrawal = event_service.get_events_for_ticket(
            self.ticket.id)
        assert len(events_after_withdrawal) == 2

        withdrawal_event = events_after_withdrawal[1]
        assert_event(withdrawal_event, 'user-withdrawn', {
            'initiator_id': str(self.owner.id),
        })

    # helpers

    def create_category(self, title):
        return category_service.create_category(self.party.id, title)


def assert_event(event, event_type, data):
    assert event.event_type == event_type
    assert event.data == data
