# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request

from ...services.countries import service as countries_service
from ...services.shop.article import service as article_service
from ...services.shop.sequence import service as sequence_service
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authentication.decorators import login_required

from .forms import assemble_articles_order_form, OrderForm
from .models.cart import Cart
from .models.order import PaymentMethod
from . import order_service


blueprint = create_blueprint('shop', __name__)


@blueprint.route('/order')
@login_required
@templated
def order_form(erroneous_form=None):
    """Show a form to order articles."""
    article_compilation = article_service \
        .get_article_compilation_for_orderable_articles(g.party.id)

    if article_compilation.is_empty():
        flash_error('Es sind keine Artikel verfügbar.')
        return {'article_compilation': None}

    user = g.current_user

    if erroneous_form:
        form = erroneous_form
    else:
        ArticlesOrderForm = assemble_articles_order_form(article_compilation)
        form = ArticlesOrderForm(obj=user.detail)

    country_names = countries_service.get_country_names()

    return {
        'form': form,
        'country_names': country_names,
        'article_compilation': article_compilation,
    }


@blueprint.route('/order', methods=['POST'])
@login_required
def order():
    """Order articles."""
    article_compilation = article_service \
        .get_article_compilation_for_orderable_articles(g.party.id)

    if article_compilation.is_empty():
        flash_error('Es sind keine Artikel verfügbar.')
        return order_form()

    ArticlesOrderForm = assemble_articles_order_form(article_compilation)
    form = ArticlesOrderForm(request.form)

    if not form.validate():
        return order_form(form)

    cart = form.get_cart(article_compilation)

    if cart.is_empty():
        flash_error('Es wurden keine Artikel ausgewählt.')
        return order_form(form)

    order_number = sequence_service.generate_order_number(g.party.id)
    orderer = form.get_orderer(g.current_user)
    payment_method = PaymentMethod.bank_transfer

    order_service.create_order(g.party.id, order_number, orderer,
                               payment_method, cart)

    flash_success('Deine Bestellung wurde entgegen genommen. Vielen Dank!')
    return redirect_to('snippet.order_placed')


@blueprint.route('/order_single/<uuid:article_id>')
@login_required
@templated
def order_single_form(article_id, erroneous_form=None):
    """Show a form to order a single article."""
    article = _get_article_or_404(article_id)

    article_compilation = article_service \
        .get_article_compilation_for_single_article(article, fixed_quantity=1)

    user = g.current_user
    form = erroneous_form if erroneous_form else OrderForm(obj=user.detail)
    country_names = countries_service.get_country_names()

    if article.not_directly_orderable:
        flash_error('Der Artikel kann nicht direkt bestellt werden.')
        return {
            'form': form,
            'article': None,
        }

    if order_service.has_user_placed_orders(user.id, g.party.id):
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
        'country_names': country_names,
        'article': article,
        'article_compilation': article_compilation,
    }


@blueprint.route('/order_single/<uuid:article_id>', methods=['POST'])
@login_required
def order_single(article_id):
    """Order a single article."""
    article = _get_article_or_404(article_id)
    quantity = 1

    if article.not_directly_orderable:
        flash_error('Der Artikel kann nicht direkt bestellt werden.')
        return order_single_form(article.id)

    article_compilation = article_service \
        .get_article_compilation_for_single_article(article,
                                                    fixed_quantity=quantity)

    user = g.current_user

    if order_service.has_user_placed_orders(user.id, g.party.id):
        flash_error('Du kannst keine weitere Bestellung aufgeben.')
        return order_single_form(article.id)

    if article.quantity < 1 or not article.is_available:
        flash_error('Der Artikel ist nicht verfügbar.')
        return order_single_form(article.id)

    form = OrderForm(request.form)
    if not form.validate():
        return order_single_form(article.id, form)

    order_number = sequence_service.generate_order_number(g.party.id)
    orderer = form.get_orderer(user)
    payment_method = PaymentMethod.bank_transfer

    cart = Cart()
    for item in article_compilation:
        cart.add_item(item.article, item.fixed_quantity)

    order_service.create_order(g.party.id, order_number, orderer,
                               payment_method, cart)

    flash_success('Deine Bestellung wurde entgegen genommen. Vielen Dank!')
    return redirect_to('snippet.order_placed')


def _get_article_or_404(article_id):
    article = article_service.find_article(article_id)

    if article is None:
        abort(404)

    return article
