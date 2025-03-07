"""
byceps.services.shop.order.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


shop_order_signals = Namespace()


order_placed = shop_order_signals.signal('order-placed')
order_canceled = shop_order_signals.signal('order-canceled')
order_paid = shop_order_signals.signal('order-paid')
