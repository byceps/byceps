"""
byceps.blueprints.admin.shop.order.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request, Response

from .....services.brand import service as brand_service
from .....services.shop.order import (
    sequence_service as order_sequence_service,
    service as order_service,
)
from .....services.shop.order.email import service as order_email_service
from .....services.shop.order.export import service as order_export_service
from .....services.shop.order.transfer.models import PaymentMethod, PaymentState
from .....services.shop.shop import service as shop_service
from .....services.ticketing import ticket_service
from .....services.user import service as user_service
from .....signals import shop as shop_signals
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_notice, flash_success
from .....util.framework.templating import templated
from .....util.views import redirect_to, respond_no_content

from ....common.authorization.decorators import permission_required
from ....common.authorization.registry import permission_registry

from ..shop.authorization import ShopPermission
from .authorization import ShopOrderPermission
from .forms import CancelForm, MarkAsPaidForm, OrderNumberSequenceCreateForm
from .models import OrderStateFilter
from . import service


blueprint = create_blueprint('shop_order_admin', __name__)


permission_registry.register_enum(ShopOrderPermission)


@blueprint.route('/for_shop/<shop_id>', defaults={'page': 1})
@blueprint.route('/for_shop/<shop_id>/pages/<int:page>')
@permission_required(ShopOrderPermission.view)
@templated
def index_for_shop(shop_id, page):
    """List orders for that shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    per_page = request.args.get('per_page', type=int, default=15)

    search_term = request.args.get('search_term', default='').strip()

    only_payment_state = request.args.get(
        'only_payment_state', type=PaymentState.__members__.get
    )

    def _str_to_bool(value):
        valid_values = {
            'true': True,
            'false': False,
        }
        return valid_values.get(value, False)

    only_shipped = request.args.get('only_shipped', type=_str_to_bool)

    order_state_filter = OrderStateFilter.find(only_payment_state, only_shipped)

    orders = order_service.get_orders_for_shop_paginated(
        shop.id,
        page,
        per_page,
        search_term=search_term,
        only_payment_state=only_payment_state,
        only_shipped=only_shipped,
    )

    orders.items = list(service.extend_order_tuples_with_orderer(orders.items))

    return {
        'shop': shop,
        'brand': brand,
        'search_term': search_term,
        'PaymentState': PaymentState,
        'only_payment_state': only_payment_state,
        'only_shipped': only_shipped,
        'OrderStateFilter': OrderStateFilter,
        'order_state_filter': order_state_filter,
        'orders': orders,
        'render_order_payment_method': _find_order_payment_method_label,
    }


@blueprint.route('/<uuid:order_id>')
@permission_required(ShopOrderPermission.view)
@templated
def view(order_id):
    """Show a single order."""
    order = order_service.find_order_with_details(order_id)
    if order is None:
        abort(404)

    placed_by = user_service.get_user(order.placed_by_id, include_avatar=True)

    shop = shop_service.get_shop(order.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    articles_by_item_number = service.get_articles_by_item_number(order)

    events = service.get_events(order.id)

    tickets = ticket_service.find_tickets_created_by_order(order.order_number)

    return {
        'shop': shop,
        'brand': brand,
        'order': order,
        'placed_by': placed_by,
        'articles_by_item_number': articles_by_item_number,
        'events': events,
        'PaymentMethod': PaymentMethod,
        'PaymentState': PaymentState,
        'tickets': tickets,
        'render_order_payment_method': _find_order_payment_method_label,
    }


# -------------------------------------------------------------------- #
# export


@blueprint.route('/<uuid:order_id>/export')
@permission_required(ShopOrderPermission.view)
def export(order_id):
    """Export the order as an XML document."""
    xml_export = order_export_service.export_order_as_xml(order_id)

    if xml_export is None:
        abort(404)

    return Response(
        xml_export['content'], content_type=xml_export['content_type']
    )


# -------------------------------------------------------------------- #
# flags


@blueprint.route('/<uuid:order_id>/flags/invoiced', methods=['POST'])
@permission_required(ShopOrderPermission.update)
@respond_no_content
def set_invoiced_flag(order_id):
    """Mark the order as invoiced."""
    order = _get_order_or_404(order_id)
    initiator_id = g.current_user.id

    order_service.set_invoiced_flag(order.id, initiator_id)

    flash_success(
        f'Bestellung {order.order_number} wurde '
        'als in Rechnung gestellt markiert.'
    )


@blueprint.route('/<uuid:order_id>/flags/invoiced', methods=['DELETE'])
@permission_required(ShopOrderPermission.update)
@respond_no_content
def unset_invoiced_flag(order_id):
    """Mark the order as not invoiced."""
    order = _get_order_or_404(order_id)
    initiator_id = g.current_user.id

    order_service.unset_invoiced_flag(order.id, initiator_id)

    flash_success(
        f'Bestellung {order.order_number} wurde '
        'als nicht in Rechnung gestellt markiert.'
    )


@blueprint.route('/<uuid:order_id>/flags/shipped', methods=['POST'])
@permission_required(ShopOrderPermission.update)
@respond_no_content
def set_shipped_flag(order_id):
    """Mark the order as shipped."""
    order = _get_order_or_404(order_id)
    initiator_id = g.current_user.id

    order_service.set_shipped_flag(order.id, initiator_id)

    flash_success(
        f'Bestellung {order.order_number} wurde als verschickt markiert.'
    )


@blueprint.route('/<uuid:order_id>/flags/shipped', methods=['DELETE'])
@permission_required(ShopOrderPermission.update)
@respond_no_content
def unset_shipped_flag(order_id):
    """Mark the order as not shipped."""
    order = _get_order_or_404(order_id)
    initiator_id = g.current_user.id

    order_service.unset_shipped_flag(order.id, initiator_id)

    flash_success(
        f'Bestellung {order.order_number} wurde als nicht verschickt markiert.'
    )


# -------------------------------------------------------------------- #
# cancel


@blueprint.route('/<uuid:order_id>/cancel')
@permission_required(ShopOrderPermission.cancel)
@templated
def cancel_form(order_id, erroneous_form=None):
    """Show form to cancel an order."""
    order = _get_order_or_404(order_id)

    if order.is_canceled:
        flash_error(
            'Die Bestellung ist bereits storniert worden; '
            'der Bezahlstatus kann nicht mehr geändert werden.'
        )
        return redirect_to('.view', order_id=order.id)

    shop = shop_service.get_shop(order.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    form = erroneous_form if erroneous_form else CancelForm()

    return {
        'shop': shop,
        'brand': brand,
        'order': order,
        'form': form,
    }


@blueprint.route('/<uuid:order_id>/cancel', methods=['POST'])
@permission_required(ShopOrderPermission.cancel)
def cancel(order_id):
    """Set the payment status of a single order to 'canceled' and
    release the respective article quantities.
    """
    order = _get_order_or_404(order_id)

    form = CancelForm(request.form)
    if not form.validate():
        return cancel_form(order_id, form)

    reason = form.reason.data.strip()
    send_email = form.send_email.data

    try:
        event = order_service.cancel_order(order.id, g.current_user.id, reason)
    except order_service.OrderAlreadyCanceled:
        flash_error(
            'Die Bestellung ist bereits storniert worden; '
            'der Bezahlstatus kann nicht mehr geändert werden.'
        )
        return redirect_to('.view', order_id=order.id)

    flash_success(
        'Die Bestellung wurde als storniert markiert und die betroffenen '
        'Artikel in den entsprechenden Stückzahlen wieder zur Bestellung '
        'freigegeben.'
    )

    if send_email:
        order_email_service.send_email_for_canceled_order_to_orderer(order.id)
    else:
        flash_notice(
            'Es wurde keine E-Mail an den/die Auftraggeber/in versendet.'
        )

    shop_signals.order_canceled.send(None, event=event)

    return redirect_to('.view', order_id=order.id)


# -------------------------------------------------------------------- #
# mark as paid


@blueprint.route('/<uuid:order_id>/mark_as_paid')
@permission_required(ShopOrderPermission.mark_as_paid)
@templated
def mark_as_paid_form(order_id, erroneous_form=None):
    """Show form to mark an order as paid."""
    order = _get_order_or_404(order_id)

    if order.is_paid:
        flash_error('Die Bestellung ist bereits als bezahlt markiert worden.')
        return redirect_to('.view', order_id=order.id)

    shop = shop_service.get_shop(order.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    form = erroneous_form if erroneous_form else MarkAsPaidForm()

    return {
        'shop': shop,
        'brand': brand,
        'order': order,
        'form': form,
    }


@blueprint.route('/<uuid:order_id>/mark_as_paid', methods=['POST'])
@permission_required(ShopOrderPermission.mark_as_paid)
def mark_as_paid(order_id):
    """Set the payment status of a single order to 'paid'."""
    order = _get_order_or_404(order_id)

    form = MarkAsPaidForm(request.form)
    if not form.validate():
        return mark_as_paid_form(order_id, form)

    payment_method = PaymentMethod[form.payment_method.data]
    updated_by_id = g.current_user.id

    try:
        event = order_service.mark_order_as_paid(
            order.id, payment_method, updated_by_id
        )
    except order_service.OrderAlreadyMarkedAsPaid:
        flash_error('Die Bestellung ist bereits als bezahlt markiert worden.')
        return redirect_to('.view', order_id=order.id)

    flash_success('Die Bestellung wurde als bezahlt markiert.')

    order_email_service.send_email_for_paid_order_to_orderer(order.id)

    shop_signals.order_paid.send(None, event=event)

    return redirect_to('.view', order_id=order.id)


# -------------------------------------------------------------------- #
# email


@blueprint.route(
    '/<uuid:order_id>/resend_incoming_order_email', methods=['POST']
)
@permission_required(ShopOrderPermission.update)
@respond_no_content
def resend_email_for_incoming_order_to_orderer(order_id):
    """Resend the e-mail to the orderer to confirm that the order was placed."""
    order = _get_order_or_404(order_id)

    order_email_service.send_email_for_incoming_order_to_orderer(order.id)

    flash_success('Die E-Mail-Eingangsbestätigung wurde erneut versendet.')


# -------------------------------------------------------------------- #
# order number sequences


@blueprint.route('/number_sequences/for_shop/<shop_id>/create')
@permission_required(ShopPermission.update)
@templated
def create_number_sequence_form(shop_id, erroneous_form=None):
    """Show form to create an order number sequence."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    form = erroneous_form if erroneous_form else OrderNumberSequenceCreateForm()

    return {
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.route('/number_sequences/for_shop/<shop_id>', methods=['POST'])
@permission_required(ShopPermission.update)
def create_number_sequence(shop_id):
    """Create an order number sequence."""
    shop = _get_shop_or_404(shop_id)

    form = OrderNumberSequenceCreateForm(request.form)
    if not form.validate():
        return create_number_sequence_form(shop_id, form)

    prefix = form.prefix.data.strip()

    sequence_id = order_sequence_service.create_order_number_sequence(
        shop.id, prefix
    )
    if sequence_id is None:
        flash_error(
            'Die Bestellnummer-Sequenz konnte nicht angelegt werden. '
            f'Ist das Präfix "{prefix}" bereits definiert?'
        )
        return create_number_sequence_form(shop.id, form)

    flash_success(
        f'Die Bestellnummer-Sequenz mit dem Präfix "{prefix}" wurde angelegt.'
    )
    return redirect_to('.index_for_shop', shop_id=shop.id)


# -------------------------------------------------------------------- #
# helpers


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop


def _get_order_or_404(order_id):
    order = order_service.find_order(order_id)

    if order is None:
        abort(404)

    return order


def _find_order_payment_method_label(payment_method):
    return order_service.find_payment_method_label(payment_method)
