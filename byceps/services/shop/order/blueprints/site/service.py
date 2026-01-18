"""
byceps.services.shop.order.blueprints.site.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from flask_babel import gettext
from moneyed import Currency

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.catalog import catalog_service
from byceps.services.shop.catalog.models import CatalogID
from byceps.services.shop.order import (
    order_checkout_service,
    signals as shop_order_signals,
)
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.product import product_service
from byceps.services.shop.product.errors import NoProductsAvailableError
from byceps.services.shop.product.models import (
    Product,
    ProductCollection,
    ProductCompilation,
    ProductCompilationBuilder,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import Storefront
from byceps.util.result import Err, Ok, Result


def get_collections(
    storefront: Storefront,
) -> Result[list[ProductCollection], str]:
    if storefront.catalog:
        return Ok(_get_collections_from_catalog(storefront.catalog.id))
    else:
        return _get_collections_from_shop(storefront.shop_id)


def _get_collections_from_catalog(
    catalog_id: CatalogID,
) -> list[ProductCollection]:
    return catalog_service.get_product_collections_for_catalog(
        catalog_id,
        only_currently_available=True,
        only_directly_orderable=True,
        only_not_requiring_separate_order=True,
    )


def _get_collections_from_shop(
    shop_id: ShopID,
) -> Result[list[ProductCollection], str]:
    match product_service.get_product_compilation_for_orderable_products(
        shop_id
    ):
        case Ok(compilation):
            collection = (
                product_service.get_product_collection_for_product_compilation(
                    '', compilation
                )
            )
            return Ok([collection])
        case Err(e):
            if isinstance(e, NoProductsAvailableError):
                return Err(gettext('No products are available.'))
            else:
                return Err(gettext('An unknown error has occurred.'))


def get_products_from_collections(
    collections: list[ProductCollection],
) -> list[Product]:
    return [
        item.product for collection in collections for item in collection.items
    ]


def build_product_compilation(
    products: Iterable[Product],
) -> ProductCompilation:
    builder = ProductCompilationBuilder()

    for product in products:
        builder.append_product(product)

    return builder.build()


def create_cart_from_product_compilation(
    currency: Currency, compilation: ProductCompilation
) -> Cart:
    cart = Cart(currency)

    for item in compilation:
        cart.add_item(item.product, item.fixed_quantity)

    return cart


def place_order(storefront, orderer, cart) -> Result[Order, None]:
    placement_result = order_checkout_service.place_order(
        storefront, orderer, cart
    )
    if placement_result.is_err():
        return Err(None)

    order, event = placement_result.unwrap()

    order_email_service.send_email_for_incoming_order_to_orderer(order)

    shop_order_signals.order_placed.send(None, event=event)

    return Ok(order)
