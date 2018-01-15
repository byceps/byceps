"""
byceps.services.shop.order.models.order.payment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum


PaymentMethod = Enum('PaymentMethod', ['bank_transfer', 'cash', 'direct_debit'])


PaymentState = Enum('PaymentState', [
    'open',
    'canceled_before_paid',
    'paid',
    'canceled_after_paid',
])
