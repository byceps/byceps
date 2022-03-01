"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

from flask import Flask
import pytest
from pytest import raises

from byceps.events.ticketing import TicketsSold
from byceps.services.shop.article.transfer.models import Article
from byceps.services.shop.order import action_registry_service
from byceps.services.shop.order import log_service as order_log_service
from byceps.services.shop.order.transfer.order import Order, Orderer
from byceps.services.shop.shop.transfer.models import Shop
from byceps.services.shop.storefront.transfer.models import Storefront
from byceps.services.ticketing import ticket_service
from byceps.services.ticketing.ticket_creation_service import (
    TicketCreationFailed,
)
from byceps.services.ticketing.transfer.models import TicketCategory
from byceps.services.user.transfer.models import User

from .helpers import get_tickets_for_order, mark_order_as_paid, place_order


@pytest.fixture
def article(make_article, shop: Shop) -> Article:
    return make_article(shop.id)


@pytest.fixture(scope='module')
def ticket_quantity() -> int:
    return 4


@pytest.fixture
def order(
    article: Article, ticket_quantity, storefront: Storefront, orderer: Orderer
) -> Order:
    articles_with_quantity = [(article, ticket_quantity)]
    return place_order(storefront.id, orderer, articles_with_quantity)


@pytest.fixture
def order_action(article: Article, ticket_category: TicketCategory) -> None:
    action_registry_service.register_tickets_creation(
        article.item_number, ticket_category.id
    )


@patch('byceps.signals.ticketing.tickets_sold.send')
def test_create_tickets(
    tickets_sold_signal_send_mock,
    admin_app: Flask,
    article: Article,
    ticket_category: TicketCategory,
    ticket_quantity: int,
    admin_user: User,
    orderer_user: User,
    orderer: Orderer,
    order: Order,
    order_action,
) -> None:
    tickets_before_paid = get_tickets_for_order(order)
    assert len(tickets_before_paid) == 0

    shop_order_paid_event = mark_order_as_paid(order.id, admin_user.id)

    tickets_after_paid = get_tickets_for_order(order)
    assert len(tickets_after_paid) == ticket_quantity

    for ticket in tickets_after_paid:
        assert ticket.owned_by_id == orderer.user_id
        assert ticket.used_by_id == orderer.user_id

    log_entries = order_log_service.get_entries_for_order(order.id)
    ticket_created_log_entries = [
        entry for entry in log_entries if entry.event_type == 'ticket-created'
    ]
    assert len(ticket_created_log_entries) == ticket_quantity

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


@patch('byceps.services.ticketing.ticket_code_service._generate_ticket_code')
def test_create_tickets_with_same_code_fails(
    generate_ticket_code_mock,
    admin_app: Flask,
    article: Article,
    ticket_category: TicketCategory,
    ticket_quantity: int,
    admin_user: User,
    orderer: Orderer,
    order: Order,
    order_action,
) -> None:
    generate_ticket_code_mock.side_effect = lambda: 'EQUAL'

    with raises(TicketCreationFailed):
        mark_order_as_paid(order.id, admin_user.id)


@patch('byceps.services.ticketing.ticket_code_service._generate_ticket_code')
def test_create_tickets_with_temporarily_equal_code_and_retry_succeeds(
    generate_ticket_code_mock,
    admin_app: Flask,
    article: Article,
    ticket_category: TicketCategory,
    ticket_quantity: int,
    admin_user: User,
    orderer: Orderer,
    order: Order,
    order_action,
) -> None:
    code_generation_retries = 4  # Depends on implemented default value.
    necessary_outer_retries = 5  # Depends on argument to `retry` decorator.
    codes = ['EQUAL'] * code_generation_retries * necessary_outer_retries
    codes += ['TICK1', 'TICK2', 'TICK3', 'TICK4']
    codes_iter = iter(codes)
    generate_ticket_code_mock.side_effect = lambda: next(codes_iter)

    tickets_before_paid = get_tickets_for_order(order)
    assert len(tickets_before_paid) == 0

    mark_order_as_paid(order.id, admin_user.id)

    tickets_after_paid = get_tickets_for_order(order)
    assert len(tickets_after_paid) == ticket_quantity
