"""
byceps.services.shop.order.models.order.orderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from .....typing import UserID


@dataclass(frozen=True)
class Orderer:
    """Someone who orders articles."""

    user_id: UserID
    first_names: str
    last_name: str
    country: str
    zip_code: str
    city: str
    street: str
