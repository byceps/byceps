"""
byceps.blueprints.shop.order.signals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from blinker import Namespace


shop_signals = Namespace()


order_placed = shop_signals.signal('order-placed')
order_canceled = shop_signals.signal('order-canceled')
order_paid = shop_signals.signal('order-paid')
