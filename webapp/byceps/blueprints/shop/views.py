# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import abort, g, request

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authorization.decorators import login_required

from .forms import OrderForm
from .models import Article, Order, PaymentState
from .signals import order_placed


blueprint = create_blueprint('shop', __name__)


@blueprint.route('/order_single')
@login_required
@templated
def order_single_form(errorneous_form=None):
    """Show a form to order a single article."""
    user = g.current_user
    form = errorneous_form if errorneous_form else OrderForm(obj=user.detail)

    orders_placed_by_user = Order.query.for_current_party().filter_by(placed_by=user).count()
    if orders_placed_by_user > 0:
        flash_error('Du kannst keine weiteren Bestellung aufgeben.')
        return {
            'form': form,
            'article': None,
        }

    article_id = request.args.get('article', type=str)
    if not article_id:
        flash_error('Es wurde kein Artikel angegeben.')
        return {
            'form': form,
            'article': None,
        }

    article = Article.query.get(article_id)
    if article is None:
        flash_error('Der Artikel wurde nicht gefunden.')
        return {
            'form': form,
            'article': None,
        }

    if article.quantity < 1:
        flash_error('Der Artikel ist nicht mehr verfügbar.')
        return {
            'form': form,
            'article': None,
        }

    return {
        'form': form,
        'article': article,
    }


@blueprint.route('/order_single', methods=['POST'])
@login_required
def order_single():
    """Order a single article."""
    user = g.current_user

    orders_placed_by_user = Order.query.for_current_party().filter_by(placed_by=user).count()
    if orders_placed_by_user > 0:
        flash_error('Du kannst keine weiteren Bestellung aufgeben.')
        return order_single_form()

    article_id = request.args.get('article', type=str)
    if not article_id:
        flash_error('Es wurde kein Artikel angegeben.')
        return order_single_form()

    article = Article.query.get(article_id)
    if article is None:
        flash_error('Der Artikel wurde nicht gefunden.')
        return order_single_form()

    if article.quantity < 1:
        flash_error('Der Artikel ist nicht mehr verfügbar.')
        return order_single_form()

    form = OrderForm(request.form)
    if not form.validate():
        return order_single_form(form)

    order = Order(
        party=g.party,
        placed_by=user,
        first_names=form.first_names.data.strip(),
        last_name=form.last_name.data.strip(),
        date_of_birth=form.date_of_birth.data,
        zip_code=form.zip_code.data.strip(),
        city=form.city.data.strip(),
        street=form.street.data.strip(),
    )
    db.session.add(order)

    article_quantity = 1

    order_item = order.add_item(article, article_quantity)
    db.session.add(order_item)

    article.quantity -= article_quantity

    db.session.commit()

    flash_success('Deine Bestellung wurde entgegen genommen. Vielen Dank!')

    order_placed.send(None, order=order)

    return redirect_to('snippet.order_placed')
