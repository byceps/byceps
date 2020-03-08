"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.order import action_registry_service
from byceps.services.shop.order import event_service as order_event_service
from byceps.services.ticketing import (
    category_service as ticket_category_service,
)

from tests.services.shop.helpers import create_article

from .base import (
    get_tickets_for_order,
    mark_order_as_paid,
    OrderActionTestBase,
    place_order,
)


class CreateTicketsActionTest(OrderActionTestBase):

    def setUp(self):
        super().setUp()

        self.article = create_article(self.shop.id, quantity=10)

        self.ticket_category = ticket_category_service.create_category(
            self.party.id, 'Deluxe'
        )

    def test_create_tickets(self):
        ticket_quantity = 4

        action_registry_service.register_tickets_creation(
            self.article.item_number, self.ticket_category.id
        )

        articles_with_quantity = [(self.article, ticket_quantity)]
        order = place_order(self.shop.id, self.buyer, articles_with_quantity)

        tickets_before_paid = get_tickets_for_order(order)
        assert len(tickets_before_paid) == 0

        mark_order_as_paid(order.id, self.admin.id)

        tickets_after_paid = get_tickets_for_order(order)
        assert len(tickets_after_paid) == ticket_quantity

        for ticket in tickets_after_paid:
            assert ticket.owned_by_id == self.buyer.id
            assert ticket.used_by_id == self.buyer.id

        events = order_event_service.get_events_for_order(order.id)
        ticket_created_events = {
            event for event in events if event.event_type == 'ticket-created'
        }
        assert len(ticket_created_events) == ticket_quantity
