# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from ...util.framework import create_blueprint
from ...util.templating import templated

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry
from ..shop.models import Article, Order
from ..party.models import Party

from .authorization import ShopPermission


blueprint = create_blueprint('shop_admin', __name__)


permission_registry.register_enum(ShopPermission)


@blueprint.route('/articles')
@permission_required(ShopPermission.list_articles)
@templated
def article_index():
    """List parties to choose from."""
    parties = Party.query.all()
    return {'parties': parties}


@blueprint.route('/articles/<party_id>')
@permission_required(ShopPermission.list_articles)
@templated
def article_index_for_party(party_id):
    """List articles for that party."""
    party = Party.query.get_or_404(party_id)

    articles = Article.query.for_party(party).all()

    return {
        'party': party,
        'articles': articles,
    }


@blueprint.route('/orders')
@permission_required(ShopPermission.list_orders)
@templated
def order_index():
    """List orders."""
    parties = Party.query.all()
    return {'parties': parties}


@blueprint.route('/orders/<party_id>', defaults={'page': 1})
@blueprint.route('/orders/<party_id>/pages/<int:page>')
@permission_required(ShopPermission.list_orders)
@templated
def order_index_for_party(party_id, page):
    """List orders for that party."""
    party = Party.query.get_or_404(party_id)

    per_page = 15
    query = Order.query \
        .for_party(party) \
        .order_by(Order.created_at.desc())

    orders = query.paginate(page, per_page)

    return {
        'party': party,
        'orders': orders,
    }
