# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal

from flask import abort, current_app, g, render_template, request, Response, \
    url_for

from ...services.shop.sequence import service as sequence_service
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.money import to_two_places
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..party import service as party_service
from ..shop.models.order import PaymentState
from ..shop import article_service, order_service
from ..shop.signals import order_canceled, order_paid
from ..ticket import service as ticket_service

from .authorization import ShopArticlePermission, ShopOrderPermission
from .forms import ArticleCreateForm, ArticleUpdateForm, \
    ArticleAttachmentCreateForm, OrderCancelForm
from . import service


blueprint = create_blueprint('shop_admin', __name__)


permission_registry.register_enum(ShopArticlePermission)
permission_registry.register_enum(ShopOrderPermission)


# -------------------------------------------------------------------- #
# articles


@blueprint.route('/parties/<party_id>/articles', defaults={'page': 1})
@blueprint.route('/parties/<party_id>/articles/pages/<int:page>')
@permission_required(ShopArticlePermission.list)
@templated
def article_index_for_party(party_id, page):
    """List articles for that party."""
    party = _get_party_or_404(party_id)

    per_page = request.args.get('per_page', type=int, default=15)
    articles = article_service.get_articles_for_party_paginated(party.id, page,
                                                                per_page)

    return {
        'party': party,
        'articles': articles,
    }


@blueprint.route('/articles/<uuid:id>')
@permission_required(ShopArticlePermission.view)
@templated
def article_view(id):
    """Show a single article."""
    article = article_service.find_article_with_details(id)
    if article is None:
        abort(404)

    totals = service.count_ordered_articles(article)

    return {
        'article': article,
        'totals': totals,
        'PaymentState': PaymentState,
    }


@blueprint.route('/articles/<uuid:id>/ordered')
@permission_required(ShopArticlePermission.view)
@templated
def article_view_ordered(id):
    """List the people that have ordered this article, and the
    corresponding quantities.
    """
    article = _get_article_or_404(id)

    order_items = service.get_order_items_for_article(article)

    quantity_total = sum(item.quantity for item in order_items)

    def transform(order_item):
        user = order_item.order.placed_by
        tickets = ticket_service.find_tickets_used_by_user(user, article.party)
        quantity = order_item.quantity
        order = order_item.order
        return user, tickets, quantity, order

    users_tickets_quantities_orders = map(transform, order_items)

    return {
        'article': article,
        'quantity_total': quantity_total,
        'users_tickets_quantities_orders': users_tickets_quantities_orders,
        'now': datetime.now(),
    }


@blueprint.route('/articles/for_party/<party_id>/create')
@permission_required(ShopArticlePermission.create)
@templated
def article_create_form(party_id):
    """Show form to create an article."""
    party = _get_party_or_404(party_id)

    form = ArticleCreateForm(
        price=Decimal('0.00'),
        tax_rate=Decimal('0.19'),
        quantity=0)

    return {
        'party': party,
        'form': form,
    }


@blueprint.route('/articles/for_party/<party_id>', methods=['POST'])
@permission_required(ShopArticlePermission.create)
def article_create(party_id):
    """Create an article."""
    party = _get_party_or_404(party_id)

    form = ArticleCreateForm(request.form)

    item_number = sequence_service.generate_article_number(party)
    description = form.description.data.strip()
    price = form.price.data
    tax_rate = form.tax_rate.data
    quantity = form.quantity.data

    article = article_service.create_article(party.id, item_number, description,
                                             price, tax_rate, quantity)

    flash_success('Der Artikel "{}" wurde angelegt.', article.item_number)
    return redirect_to('.article_view', id=article.id)


@blueprint.route('/articles/<uuid:id>/update')
@permission_required(ShopArticlePermission.update)
@templated
def article_update_form(id):
    """Show form to update an article."""
    article = _get_article_or_404(id)

    form = ArticleUpdateForm(obj=article)

    return {
        'form': form,
        'article': article,
    }


@blueprint.route('/articles/<uuid:id>', methods=['POST'])
@permission_required(ShopArticlePermission.update)
def article_update(id):
    """Update an article."""
    article = _get_article_or_404(id)

    form = ArticleUpdateForm(request.form)

    description = form.description.data.strip()
    price = form.price.data
    tax_rate = form.tax_rate.data
    quantity = form.quantity.data
    max_quantity_per_order = form.max_quantity_per_order.data
    not_directly_orderable = form.not_directly_orderable.data
    requires_separate_order = form.requires_separate_order.data

    article_service.update_article(article, description, price, tax_rate,
                                   quantity, max_quantity_per_order,
                                   not_directly_orderable,
                                   requires_separate_order)

    flash_success('Der Artikel "{}" wurde aktualisiert.', article.description)
    return redirect_to('.article_view', id=article.id)


@blueprint.route('/articles/<article_id>/attachments/create')
@permission_required(ShopArticlePermission.update)
@templated
def article_attachment_create_form(article_id):
    """Show form to attach an article to another article."""
    article = _get_article_or_404(article_id)

    attachable_articles = article_service.get_attachable_articles(article)

    article_choices = list(
        (article.id, '{} – {}'.format(article.item_number, article.description))
        for article in attachable_articles)

    form = ArticleAttachmentCreateForm(quantity=0)
    form.article_to_attach_id.choices = article_choices

    return {
        'article': article,
        'form': form,
    }


@blueprint.route('/articles/<article_id>/attachments', methods=['POST'])
@permission_required(ShopArticlePermission.update)
def article_attachment_create(article_id):
    """Attach an article to another article."""
    article = _get_article_or_404(article_id)

    form = ArticleAttachmentCreateForm(request.form)

    article_to_attach_id = form.article_to_attach_id.data
    article_to_attach = article_service.find_article(article_to_attach_id)
    quantity = form.quantity.data

    article_service.attach_article(article_to_attach, quantity, article)

    flash_success(
        'Der Artikel "{}" wurde {:d} mal an den Artikel "{}" angehängt.',
        article_to_attach.item_number, quantity, article.item_number)
    return redirect_to('.article_view', id=article.id)


@blueprint.route('/articles/attachments/<uuid:id>', methods=['DELETE'])
@permission_required(ShopArticlePermission.update)
@respond_no_content_with_location
def article_attachment_remove(id):
    """Remove the attachment link from one article to another."""
    attached_article = article_service.find_attached_article(id)
    if attached_article is None:
        abort(404)

    article = attached_article.article
    attached_to_article = attached_article.attached_to_article

    article_service.unattach_article(attached_article)

    flash_success('Artikel "{}" ist nun nicht mehr an Artikel "{}" angehängt.',
                  article.item_number, attached_to_article.item_number)
    return url_for('.article_view', id=article.id)


# -------------------------------------------------------------------- #
# orders


@blueprint.route('/parties/<party_id>/orders', defaults={'page': 1})
@blueprint.route('/parties/<party_id>/orders/pages/<int:page>')
@permission_required(ShopOrderPermission.list)
@templated
def order_index_for_party(party_id, page):
    """List orders for that party."""
    party = _get_party_or_404(party_id)

    per_page = request.args.get('per_page', type=int, default=15)
    only = request.args.get('only', type=PaymentState.__getitem__)

    orders = order_service \
        .get_orders_for_party_paginated(party.id, page, per_page,
                                        only_payment_state=only)

    return {
        'party': party,
        'PaymentState': PaymentState,
        'only': only,
        'orders': orders,
    }


@blueprint.route('/orders/<uuid:id>')
@permission_required(ShopOrderPermission.view)
@templated
def order_view(id):
    """Show a single order."""
    order = order_service.find_order_with_details(id)
    if order is None:
        abort(404)

    updates = order_service.get_updates_for_order(order.order_number)

    return {
        'order': order,
        'updates': updates,
        'PaymentState': PaymentState,
    }


@blueprint.route('/orders/<uuid:id>/export')
@permission_required(ShopOrderPermission.view)
def order_export(id):
    """Export the order as an XML document."""
    order = order_service.find_order_with_details(id)
    if order is None:
        abort(404)

    now = datetime.now()

    context = {
        'order': order,
        'now': now,
        'format_export_amount': _format_export_amount,
        'format_export_datetime': _format_export_datetime,
    }

    xml = render_template('shop_admin/order_export.xml', **context)

    return Response(xml, content_type='application/xml; charset=iso-8859-1')


def _format_export_amount(amount):
    """Format the monetary amount as required by the export format
    specification.
    """
    quantized = to_two_places(amount)
    return '{:.2f}'.format(quantized)


def _format_export_datetime(dt):
    """Format date and time as required by the export format specification."""
    timezone = current_app.config['TIMEZONE']
    localized_dt = timezone.localize(dt)

    date_time, utc_offset = localized_dt.strftime('%Y-%m-%dT%H:%M:%S|%z') \
                                        .split('|', 1)

    if len(utc_offset) == 5:
        # Insert colon between hours and minutes.
        utc_offset = utc_offset[:3] + ':' + utc_offset[3:]

    return date_time + utc_offset


@blueprint.route('/orders/<uuid:id>/cancel')
@permission_required(ShopOrderPermission.update)
@templated
def order_cancel_form(id):
    """Show form to cancel an order."""
    order = _get_order_or_404(id)

    cancel_form = OrderCancelForm()

    if order.payment_state == PaymentState.canceled:
        flash_error(
            'Die Bestellung ist bereits storniert worden; '
            'der Bezahlstatus kann nicht mehr geändert werden.')
        return redirect_to('.order_view', id=order.id)

    return {
        'order': order,
        'cancel_form': cancel_form,
    }


@blueprint.route('/orders/<uuid:id>/cancel', methods=['POST'])
@permission_required(ShopOrderPermission.update)
def order_cancel(id):
    """Set the payment status of a single order to 'canceled' and
    release the respective article quantities.
    """
    order = _get_order_or_404(id)

    form = OrderCancelForm(request.form)

    reason = form.reason.data.strip()

    try:
        order_service.cancel_order(order, g.current_user.id, reason)
    except order_service.OrderAlreadyCanceled:
        flash_error(
            'Die Bestellung ist bereits storniert worden; '
            'der Bezahlstatus kann nicht mehr geändert werden.')
        return redirect_to('.order_view', id=order.id)

    flash_success(
        'Die Bestellung wurde als storniert markiert und die betroffenen '
        'Artikel in den entsprechenden Stückzahlen wieder zur Bestellung '
        'freigegeben.')

    order_canceled.send(None, order=order)

    return redirect_to('.order_view', id=order.id)


@blueprint.route('/orders/<uuid:id>/mark_as_paid')
@permission_required(ShopOrderPermission.update)
@templated
def order_mark_as_paid_form(id):
    """Show form to mark an order as paid."""
    order = _get_order_or_404(id)

    if order.payment_state == PaymentState.paid:
        flash_error('Die Bestellung ist bereits als bezahlt markiert worden.')
        return redirect_to('.order_view', id=order.id)

    return {
        'order': order,
    }


@blueprint.route('/orders/<uuid:id>/mark_as_paid', methods=['POST'])
@permission_required(ShopOrderPermission.update)
def order_mark_as_paid(id):
    """Set the payment status of a single order to 'paid'."""
    order = _get_order_or_404(id)

    try:
        order_service.mark_order_as_paid(order, g.current_user.id)
    except order_service.OrderAlreadyMarkedAsPaid:
        flash_error('Die Bestellung ist bereits als bezahlt markiert worden.')
        return redirect_to('.order_view', id=order.id)

    flash_success('Die Bestellung wurde als bezahlt markiert.')

    order_paid.send(None, order=order)

    return redirect_to('.order_view', id=order.id)


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_article_or_404(article_id):
    article = article_service.find_article(article_id)

    if article is None:
        abort(404)

    return article


def _get_order_or_404(order_id):
    order = order_service.find_order(order_id)

    if order is None:
        abort(404)

    return order
