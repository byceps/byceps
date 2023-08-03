"""
byceps.blueprints.site.shop.orders.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from flask import abort, g, request
from flask_babel import gettext

from byceps.services.brand import brand_service
from byceps.services.email import (
    email_config_service,
    email_footer_service,
    email_service,
)
from byceps.services.shop.cancelation_request import cancelation_request_service
from byceps.services.shop.order import order_payment_service, order_service
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.errors import OrderAlreadyCanceledError
from byceps.services.shop.order.models.order import PaymentState
from byceps.services.shop.storefront import storefront_service
from byceps.services.user import user_service
from byceps.signals import shop as shop_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.l10n import get_user_locale
from byceps.util.views import login_required, redirect_to

from .forms import CancelForm, RequestFullRefundForm, RequestPartialRefundForm


blueprint = create_blueprint('shop_orders', __name__)


@blueprint.get('')
@login_required
@templated
def index():
    """List orders placed by the current user in the storefront assigned
    to the current site.
    """
    storefront_id = g.site.storefront_id
    if storefront_id is not None:
        storefront = storefront_service.get_storefront(storefront_id)
        orders = order_service.get_orders_placed_by_user_for_storefront(
            g.user.id, storefront.id
        )
    else:
        orders = []

    return {
        'orders': orders,
        'PaymentState': PaymentState,
    }


@blueprint.get('/<uuid:order_id>')
@login_required
@templated
def view(order_id):
    """Show a single order (if it belongs to the current user and
    current site's storefront).
    """
    order = order_service.find_order_with_details(order_id)

    if order is None:
        abort(404)

    if not _is_order_placed_by_current_user(order):
        abort(404)

    storefront = storefront_service.get_storefront(g.site.storefront_id)
    if order.storefront_id != storefront.id:
        # Order does not belong to the current site's storefront.
        abort(404)

    cancelation_request = (
        cancelation_request_service.get_request_for_order_number(
            order.order_number
        )
    )

    template_context = {
        'order': order,
        'render_order_payment_method': _find_order_payment_method_label,
        'cancelation_request': cancelation_request,
    }

    if order.is_open:
        template_context['payment_instructions'] = _get_payment_instructions(
            order
        )

    return template_context


def _find_order_payment_method_label(payment_method):
    return order_service.find_payment_method_label(payment_method)


def _get_payment_instructions(order):
    language_code = get_user_locale(g.user)

    return order_payment_service.get_html_payment_instructions(
        order, language_code
    )


@blueprint.get('/<uuid:order_id>/cancel')
@login_required
@templated
def cancel_form(order_id, erroneous_form=None):
    """Show form to cancel an order."""
    order = _get_order_by_current_user_or_404(order_id)

    if order.is_canceled:
        flash_error(gettext('The order has already been canceled.'))
        return redirect_to('.view', order_id=order.id)

    if order.is_paid:
        flash_error(
            gettext(
                'The order has already been paid. You cannot cancel it yourself anymore.'
            )
        )
        return redirect_to('.view', order_id=order.id)

    form = erroneous_form if erroneous_form else CancelForm()

    return {
        'order': order,
        'form': form,
    }


@blueprint.post('/<uuid:order_id>/cancel')
@login_required
def cancel(order_id):
    """Set the payment state of a single order to 'canceled' and
    release the respective article quantities.
    """
    order = _get_order_by_current_user_or_404(order_id)

    if order.is_canceled:
        flash_error(gettext('The order has already been canceled.'))
        return redirect_to('.view', order_id=order.id)

    if order.is_paid:
        flash_error(
            gettext(
                'The order has already been paid. You cannot cancel it yourself anymore.'
            )
        )
        return redirect_to('.view', order_id=order.id)

    form = CancelForm(request.form)
    if not form.validate():
        return cancel_form(order_id, form)

    reason = form.reason.data.strip()

    cancelation_result = order_service.cancel_order(order.id, g.user, reason)
    if cancelation_result.is_err():
        err = cancelation_result.unwrap_err()
        if isinstance(err, OrderAlreadyCanceledError):
            flash_error(
                gettext(
                    'The order has already been canceled. The payment state cannot be changed anymore.'
                )
            )
        else:
            flash_error(gettext('An unexpected error occurred.'))
        return redirect_to('.view', order_id=order.id)

    canceled_order, event = cancelation_result.unwrap()

    flash_success(gettext('Order has been canceled.'))

    order_email_service.send_email_for_canceled_order_to_orderer(canceled_order)

    shop_signals.order_canceled.send(None, event=event)

    return redirect_to('.view', order_id=canceled_order.id)


@blueprint.get('/<uuid:order_id>/request_cancelation')
@login_required
@templated
def request_cancelation_choices(order_id):
    """Show choices to request cancelation of an order."""
    order = _get_order_by_current_user_or_404(order_id)

    if order.is_canceled:
        flash_error(gettext('The order has already been canceled.'))
        return redirect_to('.view', order_id=order.id)

    if not order.is_paid:
        flash_error('Die Bestellung wurde noch nicht bezahlt.')
        return redirect_to('.view', order_id=order.id)

    request_for_order_number = (
        cancelation_request_service.get_request_for_order_number(
            order.order_number
        )
    )
    if request_for_order_number:
        flash_error('Es liegt bereits eine Stornierungsanfrage vor.')
        return redirect_to('.view', order_id=order.id)

    return {
        'order': order,
    }


@blueprint.get('/<uuid:order_id>/request_cancelation/donate_everything')
@login_required
@templated
def donate_everything_form(order_id, erroneous_form=None):
    """Show form to donate the full amount of an order."""
    order = _get_order_by_current_user_or_404(order_id)

    if order.is_canceled:
        flash_error(gettext('The order has already been canceled.'))
        return redirect_to('.view', order_id=order.id)

    if not order.is_paid:
        flash_error('Die Bestellung wurde noch nicht bezahlt.')
        return redirect_to('.view', order_id=order.id)

    request_for_order_number = (
        cancelation_request_service.get_request_for_order_number(
            order.order_number
        )
    )
    if request_for_order_number:
        flash_error('Es liegt bereits eine Stornierungsanfrage vor.')
        return redirect_to('.view', order_id=order.id)

    return {
        'order': order,
    }


@blueprint.post('/<uuid:order_id>/request_cancelation')
@login_required
def donate_everything(order_id):
    """Donate the full amount of an order, then cancel the order."""
    order = _get_order_by_current_user_or_404(order_id)

    if order.is_canceled:
        flash_error(gettext('The order has already been canceled.'))
        return redirect_to('.view', order_id=order.id)

    if not order.is_paid:
        flash_error('Die Bestellung wurde noch nicht bezahlt.')
        return redirect_to('.view', order_id=order.id)

    request_for_order_number = (
        cancelation_request_service.get_request_for_order_number(
            order.order_number
        )
    )
    if request_for_order_number:
        flash_error('Es liegt bereits eine Stornierungsanfrage vor.')
        return redirect_to('.view', order_id=order.id)

    amount_donation = order.total_amount.amount

    cancelation_request = (
        cancelation_request_service.create_request_for_full_donation(
            order.shop_id,
            order.order_number,
            amount_donation,
        )
    )

    reason = 'Ticketrückgabe und Spende des Bestellbetrags in voller Höhe wie angefordert'

    cancelation_result = order_service.cancel_order(order.id, g.user, reason)
    if cancelation_result.is_err():
        err = cancelation_result.unwrap_err()
        if isinstance(err, OrderAlreadyCanceledError):
            flash_error(
                gettext(
                    'The order has already been canceled. The payment state cannot be changed anymore.'
                )
            )
        else:
            flash_error(gettext('An unexpected error occurred.'))
        return redirect_to('.view', order_id=order.id)

    canceled_order, event = cancelation_result.unwrap()

    cancelation_request_service.accept_request(cancelation_request.id)

    flash_success(gettext('Order has been canceled.'))

    order_email_service.send_email_for_canceled_order_to_orderer(canceled_order)

    shop_signals.order_canceled.send(None, event=event)

    return redirect_to('.view', order_id=canceled_order.id)


@blueprint.get('/<uuid:order_id>/request_partial_refund')
@login_required
@templated
def request_partial_refund_form(order_id, erroneous_form=None):
    """Show form to request a partial refund of an order."""
    order = _get_order_by_current_user_or_404(order_id)

    if order.is_canceled:
        flash_error(gettext('The order has already been canceled.'))
        return redirect_to('.view', order_id=order.id)

    if not order.is_paid:
        flash_error('Die Bestellung wurde noch nicht bezahlt.')
        return redirect_to('.view', order_id=order.id)

    request_for_order_number = (
        cancelation_request_service.get_request_for_order_number(
            order.order_number
        )
    )
    if request_for_order_number:
        flash_error('Es liegt bereits eine Stornierungsanfrage vor.')
        return redirect_to('.view', order_id=order.id)

    form = erroneous_form if erroneous_form else RequestPartialRefundForm(order)

    return {
        'order': order,
        'form': form,
    }


@blueprint.post('/<uuid:order_id>/request_partial_refund')
@login_required
def request_partial_refund(order_id):
    """Request a partial refund of an order."""
    order = _get_order_by_current_user_or_404(order_id)

    if order.is_canceled:
        flash_error(gettext('The order has already been canceled.'))
        return redirect_to('.view', order_id=order.id)

    if not order.is_paid:
        flash_error('Die Bestellung wurde noch nicht bezahlt.')
        return redirect_to('.view', order_id=order.id)

    request_for_order_number = (
        cancelation_request_service.get_request_for_order_number(
            order.order_number
        )
    )
    if request_for_order_number:
        flash_error('Es liegt bereits eine Stornierungsanfrage vor.')
        return redirect_to('.view', order_id=order.id)

    form = RequestPartialRefundForm(order, request.form)
    if not form.validate():
        return request_partial_refund_form(order_id, form)

    amount_donation = form.amount_donation.data
    amount_refund = order.total_amount.amount - amount_donation
    recipient_name = form.recipient_name.data
    recipient_iban = form.recipient_iban.data

    cancelation_request_service.create_request_for_partial_refund(
        order.shop_id,
        order.order_number,
        amount_refund,
        amount_donation,
        recipient_name,
        recipient_iban,
    )

    _send_refund_request_confirmation_email(order.order_number, amount_refund)

    flash_success('Die Stornierungsanfrage wurde übermittelt.')

    return redirect_to('.view', order_id=order.id)


@blueprint.get('/<uuid:order_id>/request_full_refund')
@login_required
@templated
def request_full_refund_form(order_id, erroneous_form=None):
    """Show form to request a full refund of an order."""
    order = _get_order_by_current_user_or_404(order_id)

    if order.is_canceled:
        flash_error(gettext('The order has already been canceled.'))
        return redirect_to('.view', order_id=order.id)

    if not order.is_paid:
        flash_error('Die Bestellung wurde noch nicht bezahlt.')
        return redirect_to('.view', order_id=order.id)

    request_for_order_number = (
        cancelation_request_service.get_request_for_order_number(
            order.order_number
        )
    )
    if request_for_order_number:
        flash_error('Es liegt bereits eine Stornierungsanfrage vor.')
        return redirect_to('.view', order_id=order.id)

    form = erroneous_form if erroneous_form else RequestFullRefundForm()

    return {
        'order': order,
        'form': form,
    }


@blueprint.post('/<uuid:order_id>/request_full_refund')
@login_required
def request_full_refund(order_id):
    """Request a full refund of an order."""
    order = _get_order_by_current_user_or_404(order_id)

    if order.is_canceled:
        flash_error(gettext('The order has already been canceled.'))
        return redirect_to('.view', order_id=order.id)

    if not order.is_paid:
        flash_error('Die Bestellung wurde noch nicht bezahlt.')
        return redirect_to('.view', order_id=order.id)

    request_for_order_number = (
        cancelation_request_service.get_request_for_order_number(
            order.order_number
        )
    )
    if request_for_order_number:
        flash_error('Es liegt bereits eine Stornierungsanfrage vor.')
        return redirect_to('.view', order_id=order.id)

    form = RequestFullRefundForm(request.form)
    if not form.validate():
        return request_full_refund_form(order_id, form)

    amount_refund = order.total_amount.amount
    recipient_name = form.recipient_name.data
    recipient_iban = form.recipient_iban.data

    cancelation_request_service.create_request_for_full_refund(
        order.shop_id,
        order.order_number,
        amount_refund,
        recipient_name,
        recipient_iban,
    )

    _send_refund_request_confirmation_email(order.order_number, amount_refund)

    flash_success('Die Stornierungsanfrage wurde übermittelt.')

    return redirect_to('.view', order_id=order.id)


def _send_refund_request_confirmation_email(
    order_number, amount_refund: Decimal
) -> None:
    email_config = email_config_service.get_config(g.brand_id)

    email_address = user_service.get_email_address_data(g.user.id)
    if (email_address is None) or not email_address.verified:
        # Ignore this situation for now.
        return

    screen_name = g.user.screen_name or 'User'

    brand = brand_service.get_brand(g.brand_id)
    language_code = get_user_locale(g.user)
    footer = email_footer_service.get_footer(brand, language_code)

    sender = email_config.sender
    recipients = [email_address.address]
    subject = 'Eingang deiner Anfrage zur Rückerstattung von Tickets'
    body = (
        f'Hallo {screen_name},\n\n'
        'wir haben deine Anfrage zur Rückerstattung deiner Bestellung '
        f'{order_number} in Höhe von {amount_refund} € erhalten.\n\n'
        'Bitte beachte, dass die Abwicklung der Rückzahlung einige Zeit '
        'in Anspruch nehmen kann. Danke für dein Verständnis.'
        '\n\n'
    ) + footer

    email_service.enqueue_email(sender, recipients, subject, body)


# helpers


def _get_order_by_current_user_or_404(order_id):
    order = order_service.find_order(order_id)

    if order is None:
        abort(404)

    if not _is_order_placed_by_current_user(order):
        abort(404)

    return order


def _is_order_placed_by_current_user(order) -> bool:
    return order.placed_by_id == g.user.id
