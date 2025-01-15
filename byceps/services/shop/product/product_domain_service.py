"""
byceps.services.shop.product.product_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

from moneyed import Money

from byceps.services.shop.shop.models import ShopID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .errors import SomeProductsLackFixedQuantityError
from .models import (
    Product,
    ProductCompilation,
    ProductID,
    ProductImage,
    ProductImageID,
    ProductNumber,
    ProductType,
    ProductTypeParams,
    ProductWithQuantity,
)


def create_product(
    shop_id: ShopID,
    item_number: ProductNumber,
    type_: ProductType,
    name: str,
    price: Money,
    tax_rate: Decimal,
    total_quantity: int,
    max_quantity_per_order: int,
    processing_required: bool,
    *,
    type_params: ProductTypeParams | None = None,
    available_from: datetime | None = None,
    available_until: datetime | None = None,
    not_directly_orderable: bool = False,
    separate_order_required: bool = False,
) -> Product:
    """Create a product."""
    product_id = ProductID(generate_uuid7())
    quantity = total_quantity  # Initialize with total quantity.

    return Product(
        id=product_id,
        shop_id=shop_id,
        item_number=item_number,
        type_=type_,
        type_params=type_params if type_params else {},
        name=name,
        price=price,
        tax_rate=tax_rate,
        available_from=available_from,
        available_until=available_until,
        total_quantity=total_quantity,
        quantity=quantity,
        max_quantity_per_order=max_quantity_per_order,
        not_directly_orderable=not_directly_orderable,
        separate_order_required=separate_order_required,
        processing_required=processing_required,
        archived=False,
    )


def is_product_available_now(product: Product) -> bool:
    """Return `True` if the product is available at this moment in time."""
    start = product.available_from
    end = product.available_until

    now = datetime.utcnow()

    return (start is None or start <= now) and (end is None or now < end)


def calculate_total_amount(
    products_with_quantities: list[ProductWithQuantity],
) -> Money:
    """Calculate total amount of products with quantities."""
    if not products_with_quantities:
        raise ValueError('No products with quantity given')

    return sum(pwq.amount for pwq in products_with_quantities)  # type: ignore[return-value]


def calculate_product_compilation_total_amount(
    compilation: ProductCompilation,
) -> Result[Money, SomeProductsLackFixedQuantityError]:
    """Calculate total amount of products and their attached products in
    the compilation.
    """
    if any(item.fixed_quantity is None for item in compilation):
        return Err(SomeProductsLackFixedQuantityError())

    products_with_quantities = [
        ProductWithQuantity(item.product, item.fixed_quantity)
        for item in compilation
    ]

    total_amount = calculate_total_amount(products_with_quantities)

    return Ok(total_amount)


def create_product_image(
    product: Product, url: str, url_preview: str, position: int
) -> ProductImage:
    """Create an image for a product."""
    image_id = ProductImageID(generate_uuid7())

    return ProductImage(
        id=image_id,
        product_id=product.id,
        url=url,
        url_preview=url_preview,
        position=position,
    )
