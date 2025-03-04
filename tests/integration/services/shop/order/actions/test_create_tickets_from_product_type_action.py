"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

import pytest

from byceps.byceps_app import BycepsApp
from byceps.services.core.events import EventParty, EventUser
from byceps.services.party.models import Party
from byceps.services.shop.order import order_log_service, order_service
from byceps.services.shop.order.models.order import Order, Orderer
from byceps.services.shop.product.models import Product
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront
from byceps.services.ticketing.events import TicketsSoldEvent
from byceps.services.ticketing.models.ticket import TicketCategory
from byceps.services.ticketing.ticket_creation_service import (
    TicketCreationFailedError,
)
from byceps.services.user.models.user import User

from tests.helpers.shop import create_ticket_product, place_order

from .helpers import get_tickets_for_order, mark_order_as_paid


@pytest.fixture()
def product(shop: Shop, ticket_category: TicketCategory) -> Product:
    return create_ticket_product(shop.id, ticket_category.id)


@pytest.fixture(scope='module')
def ticket_quantity() -> int:
    return 4


@pytest.fixture()
def order(
    product: Product,
    ticket_quantity,
    shop: Shop,
    storefront: Storefront,
    orderer: Orderer,
) -> Order:
    products_with_quantity = [(product, ticket_quantity)]
    return place_order(shop, storefront, orderer, products_with_quantity)


@patch('byceps.signals.ticketing.tickets_sold.send')
def test_create_tickets(
    tickets_sold_signal_send_mock,
    admin_app: BycepsApp,
    product: Product,
    party: Party,
    ticket_category: TicketCategory,
    ticket_quantity: int,
    admin_user: User,
    orderer: Orderer,
    order: Order,
) -> None:
    tickets_before_paid = get_tickets_for_order(order)
    assert len(tickets_before_paid) == 0

    shop_order_paid_event = mark_order_as_paid(order.id, admin_user)

    tickets_after_paid = get_tickets_for_order(order)
    assert len(tickets_after_paid) == ticket_quantity

    for ticket in tickets_after_paid:
        assert ticket.owned_by_id == orderer.user.id
        assert ticket.used_by_id == orderer.user.id

    log_entries = order_log_service.get_entries_for_order(order.id)
    ticket_created_log_entries = [
        entry for entry in log_entries if entry.event_type == 'ticket-created'
    ]
    assert len(ticket_created_log_entries) == ticket_quantity

    line_items_after = order_service.get_order(order.id).line_items
    assert len(line_items_after) == 1

    ticket_line_item = line_items_after[0]
    assert ticket_line_item.processing_result == {
        'ticket_ids': list(
            sorted(str(ticket.id) for ticket in tickets_after_paid)
        ),
    }

    tickets_sold_event = TicketsSoldEvent(
        occurred_at=shop_order_paid_event.occurred_at,
        initiator=EventUser.from_user(admin_user),
        party=EventParty.from_party(party),
        owner=EventUser.from_user(orderer.user),
        quantity=ticket_quantity,
    )
    tickets_sold_signal_send_mock.assert_called_once_with(
        None, event=tickets_sold_event
    )


@patch('byceps.services.ticketing.ticket_code_service._generate_ticket_code')
def test_create_tickets_with_same_code_fails(
    generate_ticket_code_mock,
    admin_app: BycepsApp,
    product: Product,
    ticket_category: TicketCategory,
    ticket_quantity: int,
    admin_user: User,
    orderer: Orderer,
    order: Order,
) -> None:
    generate_ticket_code_mock.side_effect = lambda: 'EQUAL'  # noqa: E731

    with pytest.raises(TicketCreationFailedError):
        mark_order_as_paid(order.id, admin_user)


@patch('byceps.services.ticketing.ticket_code_service._generate_ticket_code')
def test_create_tickets_with_temporarily_equal_code_and_retry_succeeds(
    generate_ticket_code_mock,
    admin_app: BycepsApp,
    product: Product,
    ticket_category: TicketCategory,
    ticket_quantity: int,
    admin_user: User,
    orderer: Orderer,
    order: Order,
) -> None:
    code_generation_retries = 4  # Depends on implemented default value.
    necessary_outer_retries = 5  # Depends on argument to `retry` decorator.
    codes = ['EQUAL'] * code_generation_retries * necessary_outer_retries
    codes += ['TCKT1', 'TCKT2', 'TCKT3', 'TCKT4']
    codes_iter = iter(codes)
    generate_ticket_code_mock.side_effect = lambda: next(codes_iter)  # noqa: E731

    tickets_before_paid = get_tickets_for_order(order)
    assert len(tickets_before_paid) == 0

    mark_order_as_paid(order.id, admin_user)

    tickets_after_paid = get_tickets_for_order(order)
    assert len(tickets_after_paid) == ticket_quantity
