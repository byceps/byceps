# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import abort, g, request

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import login_required

from .forms import assemble_articles_order_form, OrderForm
from .models import Article, Order, PaymentState
from .service import create_order, generate_order_number, \
    get_orderable_articles, has_user_placed_orders
from .signals import order_placed


blueprint = create_blueprint('shop', __name__)


@blueprint.route('/order')
@login_required
@templated
def order_form(erroneous_form=None):
    """Show a form to order articles."""
    articles = get_orderable_articles()
    ArticlesOrderForm = assemble_articles_order_form(articles)

    user = g.current_user
    form = erroneous_form if erroneous_form else ArticlesOrderForm(obj=user.detail)

    return {
        'form': form,
        'articles': articles,
    }

@blueprint.route('/order', methods=['POST'])
@login_required
def order():
    """Order articles."""
    articles = get_orderable_articles()
    ArticlesOrderForm = assemble_articles_order_form(articles)

    form = ArticlesOrderForm(request.form)
    if not form.validate():
        return order_form(form)

    cart = form.get_cart(articles)
    if cart.is_empty():
        flash_error('Es wurden keine Artikel ausgewählt.')
        return order_form(form)

    order_number = generate_order_number(g.party)
    user = g.current_user
    orderer = form.get_orderer(user)

    order = create_order(g.party, order_number, orderer)
    db.session.add(order)

    for item in cart.get_items():
        article = item.article
        quantity = item.quantity

        article.quantity -= quantity

        order_item = order.add_item(article, quantity)
        db.session.add(order_item)

    db.session.commit()
    flash_success('Deine Bestellung wurde entgegen genommen. Vielen Dank!')
    order_placed.send(None, order=order)
    return redirect_to('snippet.order_placed')


@blueprint.route('/order_single/<uuid:article_id>')
@login_required
@templated
def order_single_form(article_id, erroneous_form=None):
    """Show a form to order a single article."""
    article = Article.query.get_or_404(article_id)

    user = g.current_user
    form = erroneous_form if erroneous_form else OrderForm(obj=user.detail)

    if has_user_placed_orders(user):
        flash_error('Du kannst keine weitere Bestellung aufgeben.')
        return {
            'form': form,
            'article': None,
        }

    if article.quantity < 1 or not article.is_available:
        flash_error('Der Artikel ist nicht verfügbar.')
        return {
            'form': form,
            'article': None,
        }

    return {
        'form': form,
        'article': article,
    }


@blueprint.route('/order_single/<uuid:article_id>', methods=['POST'])
@login_required
def order_single(article_id):
    """Order a single article."""
    article = Article.query.get_or_404(article_id)

    user = g.current_user

    if has_user_placed_orders(user):
        flash_error('Du kannst keine weitere Bestellung aufgeben.')
        return order_single_form(article.id)

    if article.quantity < 1 or not article.is_available:
        flash_error('Der Artikel ist nicht verfügbar.')
        return order_single_form(article.id)

    form = OrderForm(request.form)
    if not form.validate():
        return order_single_form(article.id, form)

    orderer = form.get_orderer(user)
    order_number = generate_order_number(g.party)

    order = create_order(g.party, order_number, orderer)
    db.session.add(order)

    article_quantity = 1

    order_item = order.add_item(article, article_quantity)
    db.session.add(order_item)

    article.quantity -= article_quantity

    db.session.commit()

    flash_success('Deine Bestellung wurde entgegen genommen. Vielen Dank!')

    order_placed.send(None, order=order)

    return redirect_to('snippet.order_placed')
