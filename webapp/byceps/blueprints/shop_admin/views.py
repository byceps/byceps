# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal
from operator import attrgetter

from flask import current_app, render_template, request, Response

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.money import to_two_places
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..shop.models.article import Article, AttachedArticle
from ..shop.models.order import Order, OrderItem, PaymentState
from ..shop.service import generate_article_number
from ..shop.signals import order_canceled, order_paid
from ..ticket.service import find_ticket_for_user
from ..party.models import Party

from .authorization import ShopArticlePermission, ShopOrderPermission
from .forms import ArticleCreateForm, ArticleUpdateForm, \
    ArticleAttachmentCreateForm, OrderCancelForm
from . import service


blueprint = create_blueprint('shop_admin', __name__)


permission_registry.register_enum(ShopArticlePermission)
permission_registry.register_enum(ShopOrderPermission)


@blueprint.route('/articles')
@permission_required(ShopArticlePermission.list)
@templated
def article_index():
    """List parties to choose from."""
    parties_with_article_counts = service.get_parties_with_article_counts()

    return {
        'parties_with_article_counts': parties_with_article_counts,
    }


@blueprint.route('/parties/<party_id>/articles', defaults={'page': 1})
@blueprint.route('/parties/<party_id>/articles/pages/<int:page>')
@permission_required(ShopArticlePermission.list)
@templated
def article_index_for_party(party_id, page):
    """List articles for that party."""
    party = Party.query.get_or_404(party_id)

    per_page = request.args.get('per_page', type=int, default=15)
    query = Article.query \
        .for_party(party) \
        .order_by(Article.description)

    articles = query.paginate(page, per_page)

    return {
        'party': party,
        'articles': articles,
    }


@blueprint.route('/articles/<uuid:id>')
@permission_required(ShopArticlePermission.view)
@templated
def article_view(id):
    """Show a single article."""
    article = Article.query \
        .options(
            db.joinedload('party'),
            db.joinedload('articles_attached_to').joinedload('article'),
            db.joinedload('attached_articles').joinedload('article'),
        ) \
        .get_or_404(id)

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
    article = Article.query.get_or_404(id)

    order_items = OrderItem.query \
        .filter_by(article=article) \
        .options(
            db.joinedload('order.placed_by').joinedload('detail'),
            db.joinedload('order').joinedload('party'),
        ) \
        .all()

    quantity_total = sum(item.quantity for item in order_items)

    def transform(order_item):
        user = order_item.order.placed_by
        ticket = find_ticket_for_user(user, article.party)
        quantity = order_item.quantity
        order = order_item.order
        return user, ticket, quantity, order

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
    party = Party.query.get_or_404(party_id)

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
    party = Party.query.get_or_404(party_id)
    form = ArticleCreateForm(request.form)

    item_number = generate_article_number(party)
    description = form.description.data.strip()
    price = form.price.data
    tax_rate = form.tax_rate.data
    quantity = form.quantity.data

    article = Article(party, item_number, description, price, tax_rate,
                      quantity)
    db.session.add(article)
    db.session.commit()

    flash_success('Des Artikel "{}" wurde angelegt.', article.item_number)
    return redirect_to('.article_view', id=article.id)


@blueprint.route('/articles/<uuid:id>/update')
@permission_required(ShopArticlePermission.update)
@templated
def article_update_form(id):
    """Show form to update an article."""
    article = Article.query.get_or_404(id)

    form = ArticleUpdateForm(obj=article)

    return {
        'form': form,
        'article': article,
    }


@blueprint.route('/articles/<uuid:id>', methods=['POST'])
@permission_required(ShopArticlePermission.update)
def article_update(id):
    """Update an article."""
    form = ArticleUpdateForm(request.form)

    article = Article.query.get_or_404(id)
    article.description = form.description.data.strip()
    article.price = form.price.data
    article.tax_rate = form.tax_rate.data
    article.quantity = form.quantity.data
    article.max_quantity_per_order = form.max_quantity_per_order.data
    article.not_directly_orderable = form.not_directly_orderable.data
    article.requires_separate_order = form.requires_separate_order.data
    db.session.commit()

    flash_success('Der Artikel "{}" wurde aktualisiert.', article.description)
    return redirect_to('.article_view', id=article.id)


@blueprint.route('/articles/<article_id>/attachments/create')
@permission_required(ShopArticlePermission.update)
@templated
def article_attachment_create_form(article_id):
    """Show form to attach an article to another article."""
    article = Article.query.get_or_404(article_id)

    attached_articles = {attached.article for attached in article.attached_articles}
    unattachable_articles = {article} | attached_articles
    unattachable_article_ids = {article.id for article in unattachable_articles}
    attachable_articles = Article.query \
        .for_party(article.party) \
        .filter(db.not_(Article.id.in_(unattachable_article_ids))) \
        .order_by(Article.item_number) \
        .all()
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
    article = Article.query.get_or_404(article_id)
    form = ArticleAttachmentCreateForm(request.form)

    article_to_attach_id = form.article_to_attach_id.data
    article_to_attach = Article.query.get(article_to_attach_id)
    quantity = form.quantity.data

    attached_article = AttachedArticle(article_to_attach, quantity, article)
    db.session.add(attached_article)
    db.session.commit()

    flash_success(
        'Der Artikel "{}" wurde {:d} mal an den Artikel "{}" angehängt.',
        article_to_attach.item_number, quantity, article.item_number)
    return redirect_to('.article_view', id=article.id)


@blueprint.route('/orders')
@permission_required(ShopOrderPermission.list)
@templated
def order_index():
    """List orders."""
    parties_with_order_counts = service.get_parties_with_order_counts()

    return {
        'parties_with_order_counts': parties_with_order_counts,
        'PaymentState': PaymentState,
    }


@blueprint.route('/parties/<party_id>/orders', defaults={'page': 1})
@blueprint.route('/parties/<party_id>/orders/pages/<int:page>')
@permission_required(ShopOrderPermission.list)
@templated
def order_index_for_party(party_id, page):
    """List orders for that party."""
    party = Party.query.get_or_404(party_id)

    per_page = request.args.get('per_page', type=int, default=15)
    query = Order.query \
        .for_party(party) \
        .options(
            db.joinedload('placed_by'),
        ) \
        .order_by(Order.created_at.desc())

    only = request.args.get('only', type=PaymentState.__getitem__)
    if only is not None:
        query = query.filter_by(_payment_state=only.name)

    orders = query.paginate(page, per_page)

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
    order = Order.query \
        .options(
            db.joinedload('party'),
            db.joinedload('items'),
        ) \
        .get_or_404(id)

    return {
        'order': order,
        'PaymentState': PaymentState,
    }


@blueprint.route('/orders/<uuid:id>/export')
@permission_required(ShopOrderPermission.view)
def order_export(id):
    """Export the order as an XML document."""
    order = Order.query \
        .options(
            db.joinedload('items'),
        ) \
        .get_or_404(id)

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


@blueprint.route('/orders/<uuid:id>/update_payment')
@permission_required(ShopOrderPermission.update)
@templated
def order_update_payment_form(id):
    """Show form to update an order's payment state."""
    order = Order.query.get_or_404(id)
    cancel_form = OrderCancelForm()

    if order.payment_state != PaymentState.open:
        flash_error(
            'Die Bestellung ist bereits abgeschlossen; '
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
    form = OrderCancelForm(request.form)
    reason = form.reason.data.strip()

    order = Order.query.get_or_404(id)

    if order.payment_state != PaymentState.open:
        flash_error(
            'Die Bestellung ist bereits abgeschlossen; '
            'der Bezahlstatus kann nicht mehr geändert werden.')
        return redirect_to('.order_view', id=order.id)

    order.cancel(reason)

    # Make the reserved quantity of articles available again.
    for item in order.items:
        item.article.quantity += item.quantity

    db.session.commit()

    flash_success(
        'Die Bestellung wurde als storniert markiert und die betroffenen '
        'Artikel in den entsprechenden Stückzahlen wieder zur Bestellung '
        'freigegeben.')

    order_canceled.send(None, order=order)

    return redirect_to('.order_view', id=order.id)


@blueprint.route('/orders/<uuid:id>/mark_as_paid', methods=['POST'])
@permission_required(ShopOrderPermission.update)
def order_mark_as_paid(id):
    """Set the payment status of a single order to 'paid'."""
    order = Order.query.get_or_404(id)

    if order.payment_state != PaymentState.open:
        flash_error(
            'Die Bestellung ist bereits abgeschlossen; '
            'der Bezahlstatus kann nicht mehr geändert werden.')
        return redirect_to('.order_view', id=order.id)

    order.mark_as_paid()
    db.session.commit()

    flash_success('Die Bestellung wurde als bezahlt markiert.')

    order_paid.send(None, order=order)

    return redirect_to('.order_view', id=order.id)
