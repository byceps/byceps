"""
byceps.blueprints.admin.shop.order.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request, Response
from flask_babel import gettext

from .....services.brand import brand_service
from .....services.shop.order import (
    order_invoice_service,
    order_log_service,
    order_sequence_service,
    order_service,
)
from .....services.shop.order.email import order_email_service
from .....services.shop.order.export import order_export_service
from .....services.shop.order.transfer.order import PaymentState
from .....services.shop.shop import shop_service
from .....services.ticketing import ticket_service
from .....services.user import user_service
from .....signals import shop as shop_signals
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_notice, flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to, respond_no_content

from .forms import (
    AddNoteForm,
    CancelForm,
    MarkAsPaidForm,
    OrderNumberSequenceCreateForm,
)
from .models import OrderStateFilter
from . import service


blueprint = create_blueprint('shop_order_admin', __name__)


@blueprint.get('/for_shop/<shop_id>', defaults={'page': 1})
@blueprint.get('/for_shop/<shop_id>/pages/<int:page>')
@permission_required('shop_order.view')
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

    only_overdue = request.args.get('only_overdue', type=_str_to_bool)
    only_processed = request.args.get('only_processed', type=_str_to_bool)

    order_state_filter = OrderStateFilter.find(
        only_payment_state, only_overdue, only_processed
    )

    orders = order_service.get_orders_for_shop_paginated(
        shop.id,
        page,
        per_page,
        search_term=search_term,
        only_payment_state=only_payment_state,
        only_overdue=only_overdue,
        only_processed=only_processed,
    )

    orders.items = list(service.extend_order_tuples_with_orderer(orders.items))

    return {
        'shop': shop,
        'brand': brand,
        'per_page': per_page,
        'search_term': search_term,
        'PaymentState': PaymentState,
        'only_payment_state': only_payment_state,
        'only_overdue': only_overdue,
        'only_processed': only_processed,
        'OrderStateFilter': OrderStateFilter,
        'order_state_filter': order_state_filter,
        'orders': orders,
        'render_order_payment_method': _find_order_payment_method_label,
    }


@blueprint.get('/<uuid:order_id>')
@permission_required('shop_order.view')
@templated
def view(order_id):
    """Show a single order."""
    order = order_service.find_order_with_details(order_id)
    if order is None:
        abort(404)

    placed_by = user_service.get_user(order.placed_by_id, include_avatar=True)

    shop = shop_service.get_shop(order.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    invoices = order_invoice_service.get_invoices_for_order(order.id)

    log_entries = service.get_enriched_log_entry_data_for_order(order.id)

    tickets = ticket_service.find_tickets_created_by_order(order.order_number)

    return {
        'shop': shop,
        'brand': brand,
        'order': order,
        'placed_by': placed_by,
        'invoices': invoices,
        'log_entries': log_entries,
        'PaymentState': PaymentState,
        'tickets': tickets,
        'render_order_payment_method': _find_order_payment_method_label,
    }


# -------------------------------------------------------------------- #
# export


@blueprint.get('/<uuid:order_id>/export')
@permission_required('shop_order.view')
def export(order_id):
    """Export the order as an XML document."""
    xml_export = order_export_service.export_order_as_xml(order_id)

    if xml_export is None:
        abort(404)

    return Response(
        xml_export['content'], content_type=xml_export['content_type']
    )


# -------------------------------------------------------------------- #
# notes


@blueprint.get('/<uuid:order_id>/notes/create')
@permission_required('shop_order.update')
@templated
def add_note_form(order_id, erroneous_form=None):
    """Show form to add a note to the order."""
    order = _get_order_or_404(order_id)

    shop = shop_service.get_shop(order.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    form = erroneous_form if erroneous_form else AddNoteForm()

    return {
        'shop': shop,
        'brand': brand,
        'order': order,
        'form': form,
    }


@blueprint.post('/<uuid:order_id>/notes')
@permission_required('shop_order.update')
def add_note(order_id):
    """Add a note to the order."""
    order = _get_order_or_404(order_id)

    form = AddNoteForm(request.form)
    if not form.validate():
        return add_note_form(order_id, form)

    text = form.text.data.strip()

    order_service.add_note(order.id, g.user.id, text)

    flash_success(gettext('Note has been added.'))

    return redirect_to('.view', order_id=order.id)


# -------------------------------------------------------------------- #
# flags


@blueprint.post('/<uuid:order_id>/flags/invoiced')
@permission_required('shop_order.update')
@respond_no_content
def set_invoiced_flag(order_id):
    """Mark the order as invoiced."""
    order = _get_order_or_404(order_id)
    initiator_id = g.user.id

    order_service.set_invoiced_flag(order.id, initiator_id)

    flash_success(
        gettext(
            'Order %(order_number)s has been marked as invoiced.',
            order_number=order.order_number,
        )
    )


@blueprint.delete('/<uuid:order_id>/flags/invoiced')
@permission_required('shop_order.update')
@respond_no_content
def unset_invoiced_flag(order_id):
    """Mark the order as not invoiced."""
    order = _get_order_or_404(order_id)
    initiator_id = g.user.id

    order_service.unset_invoiced_flag(order.id, initiator_id)

    flash_success(
        gettext(
            'Order %(order_number)s has been marked as not invoiced.',
            order_number=order.order_number,
        )
    )


@blueprint.post('/<uuid:order_id>/flags/shipped')
@permission_required('shop_order.update')
@respond_no_content
def set_shipped_flag(order_id):
    """Mark the order as shipped."""
    order = _get_order_or_404(order_id)
    initiator_id = g.user.id

    order_service.set_shipped_flag(order.id, initiator_id)

    flash_success(
        gettext(
            'Order %(order_number)s has been marked as shipped.',
            order_number=order.order_number,
        )
    )


@blueprint.delete('/<uuid:order_id>/flags/shipped')
@permission_required('shop_order.update')
@respond_no_content
def unset_shipped_flag(order_id):
    """Mark the order as not shipped."""
    order = _get_order_or_404(order_id)
    initiator_id = g.user.id

    order_service.unset_shipped_flag(order.id, initiator_id)

    flash_success(
        gettext(
            'Order %(order_number)s has been marked as not shipped.',
            order_number=order.order_number,
        )
    )


# -------------------------------------------------------------------- #
# cancel


@blueprint.get('/<uuid:order_id>/cancel')
@permission_required('shop_order.cancel')
@templated
def cancel_form(order_id, erroneous_form=None):
    """Show form to cancel an order."""
    order = _get_order_or_404(order_id)

    if order.is_canceled:
        flash_error(
            gettext(
                'The order has already been canceled. '
                'The payment state cannot be changed anymore.'
            )
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


@blueprint.post('/<uuid:order_id>/cancel')
@permission_required('shop_order.cancel')
def cancel(order_id):
    """Set the payment state of a single order to 'canceled' and
    release the respective article quantities.
    """
    order = _get_order_or_404(order_id)

    form = CancelForm(request.form)
    if not form.validate():
        return cancel_form(order_id, form)

    reason = form.reason.data.strip()
    send_email = form.send_email.data

    try:
        event = order_service.cancel_order(order.id, g.user.id, reason)
    except order_service.OrderAlreadyCanceled:
        flash_error(
            gettext(
                'The order has already been canceled. '
                'The payment state cannot be changed anymore.'
            )
        )
        return redirect_to('.view', order_id=order.id)

    flash_success(
        gettext(
            'The order has been canceled and the corresponding articles '
            'have been made available again.'
        )
    )

    if send_email:
        order_email_service.send_email_for_canceled_order_to_orderer(order.id)
    else:
        flash_notice(gettext('No email has been sent to the orderer.'))

    shop_signals.order_canceled.send(None, event=event)

    return redirect_to('.view', order_id=order.id)


# -------------------------------------------------------------------- #
# mark as paid


@blueprint.get('/<uuid:order_id>/mark_as_paid')
@permission_required('shop_order.mark_as_paid')
@templated
def mark_as_paid_form(order_id, erroneous_form=None):
    """Show form to mark an order as paid."""
    order = _get_order_or_404(order_id)

    if order.is_paid:
        flash_error(gettext('Order is already marked as paid.'))
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


@blueprint.post('/<uuid:order_id>/mark_as_paid')
@permission_required('shop_order.mark_as_paid')
def mark_as_paid(order_id):
    """Set the payment state of a single order to 'paid'."""
    order = _get_order_or_404(order_id)

    form = MarkAsPaidForm(request.form)
    if not form.validate():
        return mark_as_paid_form(order_id, form)

    payment_method = form.payment_method.data
    updated_by_id = g.user.id

    try:
        event = order_service.mark_order_as_paid(
            order.id, payment_method, updated_by_id
        )
    except order_service.OrderAlreadyMarkedAsPaid:
        flash_error(gettext('Order is already marked as paid.'))
        return redirect_to('.view', order_id=order.id)

    flash_success(gettext('Order has been marked as paid.'))

    order_email_service.send_email_for_paid_order_to_orderer(order.id)

    shop_signals.order_paid.send(None, event=event)

    return redirect_to('.view', order_id=order.id)


# -------------------------------------------------------------------- #
# email


@blueprint.post('/<uuid:order_id>/resend_incoming_order_email')
@permission_required('shop_order.update')
@respond_no_content
def resend_email_for_incoming_order_to_orderer(order_id):
    """Resend the e-mail to the orderer to confirm that the order was placed."""
    order = _get_order_or_404(order_id)

    initiator_id = g.user.id

    order_email_service.send_email_for_incoming_order_to_orderer(order.id)

    order_log_service.create_entry(
        'order-placed-confirmation-email-resent',
        order.id,
        {
            'initiator_id': str(initiator_id),
        },
    )

    flash_success(
        gettext('Email confirmation for placed order has been sent again.')
    )


# -------------------------------------------------------------------- #
# order number sequences


@blueprint.get('/number_sequences/for_shop/<shop_id>/create')
@permission_required('shop.update')
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


@blueprint.post('/number_sequences/for_shop/<shop_id>')
@permission_required('shop.update')
def create_number_sequence(shop_id):
    """Create an order number sequence."""
    shop = _get_shop_or_404(shop_id)

    form = OrderNumberSequenceCreateForm(request.form)
    if not form.validate():
        return create_number_sequence_form(shop_id, form)

    prefix = form.prefix.data.strip()

    try:
        order_sequence_service.create_order_number_sequence(shop.id, prefix)
    except order_sequence_service.OrderNumberSequenceCreationFailed:
        flash_error(
            gettext(
                'Order number sequence could not be created. '
                'Is the prefix "%(prefix)s" already defined?',
                prefix=prefix,
            )
        )
        return create_number_sequence_form(shop.id, form)

    flash_success(
        gettext(
            'Order number sequence with prefix "%(prefix)s" has been created.',
            prefix=prefix,
        )
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
