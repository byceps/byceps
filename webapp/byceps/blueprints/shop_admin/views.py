# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from datetime import datetime

from flask import request

from ...database import db
from ...util.framework import create_blueprint, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..shop.models import Article, Order, OrderItem, PaymentState
from ..shop.signals import order_canceled, order_paid
from ..ticket.service import find_ticket_for_user
from ..party.models import Party

from .authorization import ShopArticlePermission, ShopOrderPermission
from .forms import ArticleUpdateForm
from .service import count_ordered_articles


blueprint = create_blueprint('shop_admin', __name__)


permission_registry.register_enum(ShopArticlePermission)
permission_registry.register_enum(ShopOrderPermission)


@blueprint.route('/articles')
@permission_required(ShopArticlePermission.list)
@templated
def article_index():
    """List parties to choose from."""
    parties = Party.query.all()
    return {'parties': parties}


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


@blueprint.route('/articles/<id>')
@permission_required(ShopArticlePermission.view)
@templated
def article_view(id):
    """Show a single article."""
    article = Article.query.get_or_404(id)

    return {
        'article': article,
        'totals': count_ordered_articles(article),
        'PaymentState': PaymentState,
    }


@blueprint.route('/articles/<id>/ordered')
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
            db.joinedload('order'),
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


@blueprint.route('/articles/<id>/update')
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


@blueprint.route('/articles/<id>', methods=['POST'])
@permission_required(ShopArticlePermission.update)
def article_update(id):
    """Update an article."""
    form = ArticleUpdateForm(request.form)

    article = Article.query.get_or_404(id)
    article.item_number = form.item_number.data.strip()
    article.description = form.description.data.strip()
    article.quantity = form.quantity.data
    db.session.commit()

    flash_success('Der Artikel "{}" wurde aktualisiert.', article.description)
    return redirect_to('.article_view', id=article.id)


@blueprint.route('/orders')
@permission_required(ShopOrderPermission.list)
@templated
def order_index():
    """List orders."""
    parties = Party.query.all()
    return {
        'parties': parties,
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


@blueprint.route('/orders/<id>')
@permission_required(ShopOrderPermission.view)
@templated
def order_view(id):
    """Show a single order."""
    order = Order.query.get_or_404(id)

    return {
        'order': order,
        'PaymentState': PaymentState,
    }


@blueprint.route('/orders/<id>/update_payment')
@permission_required(ShopOrderPermission.update)
@templated
def order_update_payment_form(id):
    """Show form to update an order's payment state."""
    order = Order.query.get_or_404(id)

    return {
        'order': order,
    }


@blueprint.route('/orders/<id>/cancel', methods=['POST'])
@permission_required(ShopOrderPermission.update)
def order_cancel(id):
    """Set the payment status of a single order to 'canceled' and
    release the respective article quantities.
    """
    order = Order.query.get_or_404(id)
    order.cancel()

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


@blueprint.route('/orders/<id>/mark_as_paid', methods=['POST'])
@permission_required(ShopOrderPermission.update)
def order_mark_as_paid(id):
    """Set the payment status of a single order to 'paid'."""
    order = Order.query.get_or_404(id)
    order.mark_as_paid()
    db.session.commit()

    flash_success('Die Bestellung wurde als bezahlt markiert.')

    order_paid.send(None, order=order)

    return redirect_to('.order_view', id=order.id)
