"""
byceps.services.shop.order.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CartEmptyError:
    pass


@dataclass(frozen=True)
class OrderActionFailedError:
    """The execution of an order action failed."""

    details: Any


class OrderAlreadyCanceledError:
    pass


class OrderAlreadyMarkedAsPaidError:
    pass


class OrderNotPaidError:
    pass
