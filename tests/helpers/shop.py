"""
tests.helpers.shop
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

from moneyed import EUR, Money

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_checkout_service
from byceps.services.shop.order.models.order import Order, Orderer
from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import (
    Product,
    ProductNumber,
    ProductType,
    ProductTypeParams,
)
from byceps.services.shop.shop.models import Shop, ShopID
from byceps.services.shop.storefront.models import Storefront
from byceps.services.snippet import snippet_service
from byceps.services.snippet.models import SnippetID, SnippetScope
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.services.user import user_service
from byceps.services.user.models.user import User

from . import generate_token


def create_shop_snippet(
    shop_id: ShopID,
    creator: User,
    name: str,
    language_code: str,
    body: str,
) -> SnippetID:
    scope = SnippetScope('shop', shop_id)

    version, _ = snippet_service.create_snippet(
        scope, name, language_code, creator, body
    )

    return version.snippet_id


def create_product(
    shop_id: ShopID,
    *,
    item_number: ProductNumber | None = None,
    type_: ProductType = ProductType.other,
    type_params: ProductTypeParams | None = None,
    name: str | None = None,
    price: Money | None = None,
    tax_rate: Decimal | None = None,
    available_from: datetime | None = None,
    available_until: datetime | None = None,
    total_quantity: int = 999,
    max_quantity_per_order: int = 10,
    processing_required: bool = False,
) -> Product:
    if item_number is None:
        item_number = ProductNumber(generate_token())

    if name is None:
        name = generate_token()

    if price is None:
        price = Money('24.95', EUR)

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    return product_service.create_product(
        shop_id,
        item_number,
        type_,
        name,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        processing_required,
        type_params=type_params,
        available_from=available_from,
        available_until=available_until,
    )


def create_ticket_product(
    shop_id: ShopID,
    ticket_category_id: TicketCategoryID,
    *,
    item_number: ProductNumber | None = None,
    name: str | None = None,
    price: Money | None = None,
    tax_rate: Decimal | None = None,
    available_from: datetime | None = None,
    available_until: datetime | None = None,
    total_quantity: int = 999,
    max_quantity_per_order: int = 10,
) -> Product:
    if item_number is None:
        item_number = ProductNumber(generate_token())

    if name is None:
        name = generate_token()

    if price is None:
        price = Money('24.95', EUR)

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    return product_service.create_ticket_product(
        shop_id,
        item_number,
        name,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        ticket_category_id,
        available_from=available_from,
        available_until=available_until,
    )


def create_ticket_bundle_product(
    shop_id: ShopID,
    ticket_category_id: TicketCategoryID,
    ticket_quantity: int,
    *,
    item_number: ProductNumber | None = None,
    name: str | None = None,
    price: Money | None = None,
    tax_rate: Decimal | None = None,
    available_from: datetime | None = None,
    available_until: datetime | None = None,
    total_quantity: int = 999,
    max_quantity_per_order: int = 10,
) -> Product:
    if item_number is None:
        item_number = ProductNumber(generate_token())

    if name is None:
        name = generate_token()

    if price is None:
        price = Money('24.95', EUR)

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    return product_service.create_ticket_bundle_product(
        shop_id,
        item_number,
        name,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        ticket_category_id,
        ticket_quantity,
        available_from=available_from,
        available_until=available_until,
    )


def create_orderer(user: User) -> Orderer:
    detail = user_service.get_detail(user.id)

    return Orderer(
        user=user,
        company=None,
        first_name=detail.first_name or 'n/a',
        last_name=detail.last_name or 'n/a',
        country=detail.country or 'n/a',
        zip_code=detail.zip_code or 'n/a',
        city=detail.city or 'n/a',
        street=detail.street or 'n/a',
    )


def place_order(
    shop: Shop,
    storefront: Storefront,
    orderer: Orderer,
    products_with_quantity: list[tuple[Product, int]],
) -> Order:
    cart = Cart(shop.currency)
    for product, quantity in products_with_quantity:
        cart.add_item(product, quantity)

    order, _ = order_checkout_service.place_order(
        storefront, orderer, cart
    ).unwrap()

    return order
