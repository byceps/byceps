"""
byceps.services.shop.order.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CartEmptyError:
    pass


class OrderAlreadyCanceledError:
    pass


class OrderAlreadyMarkedAsPaidError:
    pass


class OrderNotPaidError:
    pass
