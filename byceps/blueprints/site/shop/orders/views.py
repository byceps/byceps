"""
byceps.blueprints.site.shop.orders.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from .....services.shop.order.email import service as order_email_service
from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import PaymentState
from .....services.shop.storefront import service as storefront_service
from .....services.site import service as site_service
from .....services.snippet.transfer.models import Scope
from .....signals import shop as shop_signals
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.money import format_euro_amount
from .....util.views import login_required, redirect_to

from ....site.snippet.templating import render_snippet_as_partial

from .forms import CancelForm


blueprint = create_blueprint('shop_orders', __name__)


@blueprint.get('')
@login_required
@templated
def index():
    """List orders placed by the current user in the storefront assigned
    to the current site.
    """
    site = site_service.get_site(g.site_id)

    storefront_id = site.storefront_id
    if storefront_id is not None:
        storefront = storefront_service.get_storefront(storefront_id)
        orders = order_service.get_orders_placed_by_user_for_shop(
            g.user.id, storefront.shop_id
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

    site = site_service.get_site(g.site_id)
    storefront = storefront_service.get_storefront(site.storefront_id)
    if order.shop_id != storefront.shop_id:
        # Order does not belong to the current site's storefront.
        abort(404)

    template_context = {
        'order': order,
        'render_order_payment_method': _find_order_payment_method_label,
    }

    if order.is_open:
        template_context['payment_instructions'] = _get_payment_instructions(
            order
        )

    return template_context


def _find_order_payment_method_label(payment_method):
    return order_service.find_payment_method_label(payment_method)


def _get_payment_instructions(order):
    scope = Scope('shop', str(order.shop_id))

    context = {
        'order_number': order.order_number,
        'total_amount': format_euro_amount(order.total_amount),
    }

    return render_snippet_as_partial(
        'payment_instructions', scope=scope, context=context
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
    """Set the payment status of a single order to 'canceled' and
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

    try:
        event = order_service.cancel_order(order.id, g.user.id, reason)
    except order_service.OrderAlreadyCanceled:
        flash_error(
            gettext(
                'The order has already been canceled. The payment state cannot be changed anymore.'
            )
        )
        return redirect_to('.view', order_id=order.id)

    flash_success(gettext('Order has been canceled.'))

    order_email_service.send_email_for_canceled_order_to_orderer(order.id)

    shop_signals.order_canceled.send(None, event=event)

    return redirect_to('.view', order_id=order.id)


def _get_order_by_current_user_or_404(order_id):
    order = order_service.find_order(order_id)

    if order is None:
        abort(404)

    if not _is_order_placed_by_current_user(order):
        abort(404)

    return order


def _is_order_placed_by_current_user(order) -> bool:
    return order.placed_by_id == g.user.id
