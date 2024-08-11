#!/usr/bin/env python

"""Cancel open orders older than N days.

:Copyright: 2019-2024 Jan Korneffel, Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import timedelta

import click
from flask_babel import force_locale

from byceps.services.shop.order import order_command_service, order_service
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.errors import OrderAlreadyCanceledError
from byceps.services.shop.order.models.order import Order
from byceps.signals import shop as shop_signals
from byceps.util.result import Err, Ok

from _util import call_with_app_context
from _validators import validate_user_screen_name


LOCALE = 'de_DE'
MAX_ORDERS_TO_CANCEL = 100
NOTIFY_ORDERERS = True
REASON_DEFAULT = 'Das Zahlungsziel wurde überschritten. Gib eine neue Bestellung auf, falls du weiterhin Interesse an der Teilnahme hast.'


@click.command()
@click.argument('shop_id')
@click.argument('age_in_days', type=click.INT)
@click.argument('canceler', callback=validate_user_screen_name)
@click.argument('reason', default=REASON_DEFAULT)
def execute(shop_id, age_in_days: int, canceler, reason: str):
    overdue_orders = _collect_overdue_orders(shop_id, age_in_days)
    for order in overdue_orders:
        with force_locale(LOCALE):
            _cancel_order(order, canceler, reason)


def _collect_overdue_orders(shop_id, age_in_days: int) -> list[Order]:
    older_than = timedelta(days=age_in_days)
    overdue_orders = order_service.get_overdue_orders(
        shop_id,
        older_than,
        limit=MAX_ORDERS_TO_CANCEL,
    )
    click.secho(f'Found {len(overdue_orders)} overdue orders.', fg='yellow')
    return overdue_orders


def _cancel_order(order, canceler, reason: str) -> None:
    match order_command_service.cancel_order(order.id, canceler, reason):
        case Ok((_, canceled_event)):
            shop_signals.order_canceled.send(None, event=canceled_event)
            click.secho(
                f'Order {order.order_number} was successfully canceled.',
                fg='green',
            )

            if NOTIFY_ORDERERS:
                _notify_orderer(order)
        case Err(e):
            if isinstance(e, OrderAlreadyCanceledError):
                message = (
                    f'Order {order.order_number} has already been canceled.'
                )
            else:
                message = f'Order {order.order_number} could not be canceled.'
            click.secho(message, fg='red')


def _notify_orderer(order) -> None:
    order_email_service.send_email_for_canceled_order_to_orderer(order)
    click.secho(
        f'Notified orderer of canceled order {order.order_number}.', fg='green'
    )


if __name__ == '__main__':
    call_with_app_context(execute)
