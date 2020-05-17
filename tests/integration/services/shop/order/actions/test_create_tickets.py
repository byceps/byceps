"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.order import action_service, action_registry_service
from byceps.services.shop.order import event_service as order_event_service
from byceps.services.shop.order import service as order_service
from byceps.services.ticketing import ticket_service

from .base import get_tickets_for_order, mark_order_as_paid, place_order


def test_create_tickets(
    admin_app,
    party,
    shop,
    order_number_sequence_id,
    article,
    ticket_category,
    admin_user,
    orderer,
):
    ticket_quantity = 4

    action_registry_service.register_tickets_creation(
        article.item_number, ticket_category.id
    )

    articles_with_quantity = [(article, ticket_quantity)]
    order = place_order(shop.id, orderer, articles_with_quantity)

    tickets_before_paid = get_tickets_for_order(order)
    assert len(tickets_before_paid) == 0

    mark_order_as_paid(order.id, admin_user.id)

    tickets_after_paid = get_tickets_for_order(order)
    assert len(tickets_after_paid) == ticket_quantity

    for ticket in tickets_after_paid:
        assert ticket.owned_by_id == orderer.user_id
        assert ticket.used_by_id == orderer.user_id

    events = order_event_service.get_events_for_order(order.id)
    ticket_created_events = {
        event for event in events if event.event_type == 'ticket-created'
    }
    assert len(ticket_created_events) == ticket_quantity

    # Clean up.
    for ticket in tickets_after_paid:
        ticket_service.delete_ticket(ticket.id)
    order_service.delete_order(order.id)
    action_service.delete_actions(article.item_number)
