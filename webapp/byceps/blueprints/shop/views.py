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

from .forms import OrderForm
from .models import Article, Order, OrderItem, PaymentState


blueprint = create_blueprint('shop', __name__)


@blueprint.route('/order')
@templated
def order_form(errorneous_form=None):
    """Show a form to order articles."""
    user = get_current_user_or_403()
    form = errorneous_form if errorneous_form else OrderForm(obj=user.detail)
    return {'form': form}


@blueprint.route('/order', methods=['POST'])
def order():
    """Order articles."""
    user = get_current_user_or_403()

    article_id = request.args.get('article', type=str)
    article = Article.query.get(article_id)
    if article is None:
        flash_error('Der Artikel wurde nicht gefunden.')
        return order_form(form)

    form = OrderForm(request.form)
    if not form.validate():
        return order_form(form)

    order = Order(
        party=g.party,
        placed_by=user,
        first_names=form.first_names.data.strip(),
        last_name=form.last_name.data.strip(),
        date_of_birth=form.date_of_birth.data,
        zip_code=form.zip_code.data.strip(),
        city=form.city.data.strip(),
        street=form.street.data.strip(),
        payment_state=PaymentState.open,
        )
    db.session.add(order)

    article_quantity = 1

    order_item = OrderItem(
        order=order,
        article=article,
        description=article.description,
        price=article.price,
        quantity=article_quantity,
        )
    db.session.add(order_item)

    db.session.commit()

    flash_success('Deine Bestellung wurde entgegen genommen. Vielen Dank!')
    return redirect_to('snippet.order_placed')


def get_current_user_or_403():
    user = g.current_user
    if not user.is_active:
        abort(403)

    return user
