"""
byceps.services.shop.product.product_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from moneyed import Money

from byceps.util.result import Err, Ok, Result

from .errors import SomeProductsLackFixedQuantityError
from .models import Product, ProductCompilation, ProductWithQuantity


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
