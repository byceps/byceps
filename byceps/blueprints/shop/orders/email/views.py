"""
byceps.blueprints.shop.orders.email.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
"""

from .....services.shop.order.email import service as order_email_service
from .....util.framework.blueprint import create_blueprint

from ...order.signals import order_canceled, order_paid, order_placed


blueprint = create_blueprint('shop_orders_email', __name__)


@order_placed.connect
def send_email_for_incoming_order_to_orderer(sender, *, order_id=None):
    order_email_service.send_email_for_incoming_order_to_orderer(order_id)


@order_canceled.connect
def send_email_for_canceled_order_to_orderer(sender, *, order_id=None):
    order_email_service.send_email_for_canceled_order_to_orderer(order_id)


@order_paid.connect
def send_email_for_paid_order_to_orderer(sender, *, order_id=None):
    order_email_service.send_email_for_paid_order_to_orderer(order_id)
