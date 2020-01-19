"""
byceps.services.shop.order.models.order.orderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
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
