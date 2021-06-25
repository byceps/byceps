"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

import pytest
from pytest import raises

from byceps.events.ticketing import TicketsSold
from byceps.services.shop.order import action_service, action_registry_service
from byceps.services.shop.order import event_service as order_event_service
from byceps.services.shop.order import service as order_service
from byceps.services.ticketing import ticket_service
from byceps.services.ticketing.ticket_creation_service import (
    TicketCreationFailed,
)

from .helpers import get_tickets_for_order, mark_order_as_paid, place_order


@pytest.fixture(scope='module')
def ticket_quantity():
    return 4


@pytest.fixture
def order(article, ticket_quantity, storefront, orderer):
    articles_with_quantity = [(article, ticket_quantity)]
    order = place_order(storefront.id, orderer, articles_with_quantity)

    yield order

    order_service.delete_order(order.id)


@pytest.fixture
def order_action(article, ticket_category):
    action_registry_service.register_tickets_creation(
        article.item_number, ticket_category.id
    )

    yield

    action_service.delete_actions_for_article(article.item_number)


@patch('byceps.signals.ticketing.tickets_sold.send')
def test_create_tickets(
    tickets_sold_signal_send_mock,
    admin_app,
    article,
    ticket_category,
    ticket_quantity,
    admin_user,
    orderer_user,
    orderer,
    order,
    order_action,
):
    tickets_before_paid = get_tickets_for_order(order)
    assert len(tickets_before_paid) == 0

    shop_order_paid_event = mark_order_as_paid(order.id, admin_user.id)

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

    tickets_sold_event = TicketsSold(
        occurred_at=shop_order_paid_event.occurred_at,
        initiator_id=admin_user.id,
        initiator_screen_name=admin_user.screen_name,
        party_id=ticket_category.party_id,
        owner_id=orderer_user.id,
        owner_screen_name=orderer_user.screen_name,
        quantity=ticket_quantity,
    )
    tickets_sold_signal_send_mock.assert_called_once_with(
        None, event=tickets_sold_event
    )

    # Clean up.
    for ticket in tickets_after_paid:
        ticket_service.delete_ticket(ticket.id)


@patch('byceps.services.ticketing.ticket_code_service._generate_ticket_code')
def test_create_tickets_with_same_code_fails(
    generate_ticket_code_mock,
    admin_app,
    article,
    ticket_category,
    ticket_quantity,
    admin_user,
    orderer,
    order,
    order_action,
):
    generate_ticket_code_mock.side_effect = lambda: 'EQUAL'

    with raises(TicketCreationFailed):
        mark_order_as_paid(order.id, admin_user.id)


@patch('byceps.services.ticketing.ticket_code_service._generate_ticket_code')
def test_create_tickets_with_temporarily_equal_code_and_retry_succeeds(
    generate_ticket_code_mock,
    admin_app,
    article,
    ticket_category,
    ticket_quantity,
    admin_user,
    orderer,
    order,
    order_action,
):
    code_generation_retries = 4  # Depends on implemented default value.
    necessary_outer_retries = 5  # Depends on argument to `retry` decorator.
    codes = ['EQUAL'] * code_generation_retries * necessary_outer_retries
    codes += ['TCKT1', 'TCKT2', 'TCKT3', 'TCKT4']
    codes_iter = iter(codes)
    generate_ticket_code_mock.side_effect = lambda: next(codes_iter)

    tickets_before_paid = get_tickets_for_order(order)
    assert len(tickets_before_paid) == 0

    mark_order_as_paid(order.id, admin_user.id)

    tickets_after_paid = get_tickets_for_order(order)
    assert len(tickets_after_paid) == ticket_quantity

    # Clean up.
    for ticket in tickets_after_paid:
        ticket_service.delete_ticket(ticket.id)
