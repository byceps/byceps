"""
byceps.services.shop.payment.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class PaymentGateway:
    id: str
    name: str
    enabled: bool
