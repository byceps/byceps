"""Cancel open orders older than N days.

:Copyright: 2019-2025 Jan Korneffel, Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import timedelta

import click
from flask_babel import force_locale, gettext

from byceps.services.shop.order import order_command_service, order_service
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.errors import OrderAlreadyCanceledError
from byceps.services.shop.order.models.order import Order
from byceps.signals import shop as shop_signals
from byceps.util.result import Err, Ok

from _util import call_with_app_context
from _validators import validate_user_screen_name


@click.command()
@click.option('--shop-id', required=True)
@click.option('--minimum-age-in-days', required=True, type=click.INT)
@click.option('--canceler', required=True, callback=validate_user_screen_name)
@click.option('--locale', required=True, default='en')
@click.option('--reason')
@click.option('--notify/--no-notify', required=True)
@click.option('--limit', default=100)
def execute(
    shop_id,
    minimum_age_in_days: int,
    canceler,
    locale: str,
    reason: str | None,
    notify: bool,
    limit: int,
):
    overdue_orders = _collect_overdue_orders(
        shop_id, minimum_age_in_days, limit
    )
    for order in overdue_orders:
        with force_locale(locale):
            _cancel_order(order, canceler, reason, notify)


def _collect_overdue_orders(
    shop_id, minimum_age_in_days: int, limit: int
) -> list[Order]:
    older_than = timedelta(days=minimum_age_in_days)
    overdue_orders = order_service.get_overdue_orders(
        shop_id, older_than, limit=limit
    )
    click.secho(f'Found {len(overdue_orders)} overdue orders.', fg='yellow')
    return overdue_orders


def _cancel_order(order, canceler, reason: str | None, notify: bool) -> None:
    if not reason:
        reason = gettext(
            'The payment deadline has been exceed. '
            'Place a new order if you are still interested in attending.'
        )

    match order_command_service.cancel_order(order.id, canceler, reason):
        case Ok((_, canceled_event)):
            shop_signals.order_canceled.send(None, event=canceled_event)
            click.secho(
                f'Order {order.order_number} was successfully canceled.',
                fg='green',
            )

            if notify:
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
