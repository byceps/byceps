"""
byceps.services.shop.shipping.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.shop.product.models import ProductID


@dataclass(frozen=True, kw_only=True)
class ProductToShip:
    product_id: ProductID
    name: str
    quantity_paid: int
    quantity_open: int
    quantity_total: int
