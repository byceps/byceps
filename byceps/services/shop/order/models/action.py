"""
byceps.services.shop.order.models.action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from byceps.services.shop.product.models import ProductID

from .order import PaymentState


ActionParameters = dict[str, Any]


@dataclass(frozen=True)
class Action:
    id: UUID
    product_id: ProductID
    payment_state: PaymentState
    procedure_name: str
    parameters: ActionParameters
