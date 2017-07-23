"""
byceps.blueprints.shop_order.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request

from ...services.country import service as country_service
from ...services.shop.article import service as article_service
from ...services.shop.cart.models import Cart
from ...services.shop.order.models.order import PaymentMethod
from ...services.shop.order import service as order_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_error, flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..authentication.decorators import login_required

from .forms import assemble_articles_order_form, OrderForm


blueprint = create_blueprint('shop_order', __name__)


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

    user = g.current_user._user

    if erroneous_form:
        form = erroneous_form
    else:
        ArticlesOrderForm = assemble_articles_order_form(article_compilation)
        form = ArticlesOrderForm(obj=user.detail)

    country_names = country_service.get_country_names()

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

    orderer = form.get_orderer(g.current_user._user)

    try:
        order = _submit_order(orderer, cart)
    except order_service.OrderFailed:
        flash_error('Die Bestellung ist fehlgeschlagen.')
        return order_form(form)

    _flash_order_success(order)

    return redirect_to('snippet.order_placed')


@blueprint.route('/order_single/<uuid:article_id>')
@login_required
@templated
def order_single_form(article_id, erroneous_form=None):
    """Show a form to order a single article."""
    article = _get_article_or_404(article_id)

    article_compilation = article_service \
        .get_article_compilation_for_single_article(article, fixed_quantity=1)

    user = g.current_user._user
    form = erroneous_form if erroneous_form else OrderForm(obj=user.detail)
    country_names = country_service.get_country_names()

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

    user = g.current_user._user

    if order_service.has_user_placed_orders(user.id, g.party.id):
        flash_error('Du kannst keine weitere Bestellung aufgeben.')
        return order_single_form(article.id)

    if article.quantity < 1 or not article.is_available:
        flash_error('Der Artikel ist nicht verfügbar.')
        return order_single_form(article.id)

    form = OrderForm(request.form)
    if not form.validate():
        return order_single_form(article.id, form)

    orderer = form.get_orderer(user)

    cart = Cart()
    for item in article_compilation:
        cart.add_item(item.article, item.fixed_quantity)

    try:
        order = _submit_order(orderer, cart)
    except order_service.OrderFailed:
        flash_error('Die Bestellung ist fehlgeschlagen.')
        return order_form(form)

    _flash_order_success(order)

    return redirect_to('snippet.order_placed')


def _get_article_or_404(article_id):
    article = article_service.find_article(article_id)

    if article is None:
        abort(404)

    return article


def _submit_order(orderer, cart):
    payment_method = PaymentMethod.bank_transfer

    return order_service.create_order(g.party.id, orderer, payment_method, cart)


def _flash_order_success(order):
    flash_success('Deine Bestellung mit der Bestellnummer <strong>{}</strong> '
                  'wurde entgegen genommen. Vielen Dank!', order.order_number,
                  text_is_safe=True)
