"""
byceps.blueprints.shop.order.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request

from ....services.country import service as country_service
from ....services.party import service as party_service
from ....services.shop.article import service as article_service
from ....services.shop.cart.models import Cart
from ....services.shop.order.email import service as order_email_service
from ....services.shop.order import service as order_service
from ....services.shop.order.transfer.models import PaymentMethod
from ....services.shop.shop import service as shop_service
from ....services.user import service as user_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_notice, flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

from ...authentication.decorators import login_required

from .forms import assemble_articles_order_form, OrderForm
from .signals import order_placed


blueprint = create_blueprint('shop_order', __name__)


@blueprint.route('/order')
@templated
def order_form(erroneous_form=None):
    """Show a form to order articles."""
    shop = _get_shop_or_404()

    if shop.closed:
        flash_notice('Der Shop ist derzeit geschlossen.')
        return {'article_compilation': None}

    article_compilation = article_service.get_article_compilation_for_orderable_articles(
        shop.id
    )

    if article_compilation.is_empty():
        flash_error('Es sind keine Artikel verfügbar.')
        return {'article_compilation': None}

    is_logged_in = g.current_user.is_active
    if not is_logged_in:
        return list_articles(article_compilation)

    user = user_service.find_user_with_details(g.current_user.id)

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


# No route registered. Intended to be called from another view function.
@templated
def list_articles(article_compilation):
    """List articles for anonymous users to view."""
    return {
        'article_compilation': article_compilation,
    }


@blueprint.route('/order', methods=['POST'])
@login_required
def order():
    """Order articles."""
    shop = _get_shop_or_404()

    if shop.closed:
        flash_notice('Der Shop ist derzeit geschlossen.')
        return order_form()

    article_compilation = article_service.get_article_compilation_for_orderable_articles(
        shop.id
    )

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

    orderer = form.get_orderer(g.current_user.id)

    try:
        order = _place_order(shop.id, orderer, cart)
    except order_service.OrderFailed:
        flash_error('Die Bestellung ist fehlgeschlagen.')
        return order_form(form)

    _flash_order_success(order)

    return redirect_to('shop_orders.view', order_id=order.id)


@blueprint.route('/order_single/<uuid:article_id>')
@login_required
@templated
def order_single_form(article_id, erroneous_form=None):
    """Show a form to order a single article."""
    article = _get_article_or_404(article_id)

    shop = _get_shop_or_404()

    if shop.closed:
        flash_notice('Der Shop ist derzeit geschlossen.')
        return {
            'form': form,
            'article': None,
        }

    article_compilation = article_service.get_article_compilation_for_single_article(
        article, fixed_quantity=1
    )

    user = user_service.find_user_with_details(g.current_user.id)

    form = erroneous_form if erroneous_form else OrderForm(obj=user.detail)
    country_names = country_service.get_country_names()

    if article.not_directly_orderable:
        flash_error('Der Artikel kann nicht direkt bestellt werden.')
        return {
            'form': form,
            'article': None,
        }

    if order_service.has_user_placed_orders(user.id, shop.id):
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

    shop = _get_shop_or_404()

    if shop.closed:
        flash_notice('Der Shop ist derzeit geschlossen.')
        return order_single_form(article.id)

    if article.not_directly_orderable:
        flash_error('Der Artikel kann nicht direkt bestellt werden.')
        return order_single_form(article.id)

    article_compilation = article_service.get_article_compilation_for_single_article(
        article, fixed_quantity=quantity
    )

    user = g.current_user

    if order_service.has_user_placed_orders(user.id, shop.id):
        flash_error('Du kannst keine weitere Bestellung aufgeben.')
        return order_single_form(article.id)

    if article.quantity < 1 or not article.is_available:
        flash_error('Der Artikel ist nicht verfügbar.')
        return order_single_form(article.id)

    form = OrderForm(request.form)
    if not form.validate():
        return order_single_form(article.id, form)

    orderer = form.get_orderer(user.id)

    cart = Cart()
    for item in article_compilation:
        cart.add_item(item.article, item.fixed_quantity)

    try:
        order = _place_order(shop.id, orderer, cart)
    except order_service.OrderFailed:
        flash_error('Die Bestellung ist fehlgeschlagen.')
        return order_form(form)

    _flash_order_success(order)

    return redirect_to('shop_orders.view', order_id=order.id)


def _get_shop_or_404():
    if g.party_id is None:
        # No party is configured for the current site.
        abort(404)

    party = party_service.get_party(g.party_id)

    if party.shop_id is None:
        abort(404)

    return shop_service.get_shop(party.shop_id)


def _get_article_or_404(article_id):
    article = article_service.find_article(article_id)

    if article is None:
        abort(404)

    return article


def _place_order(shop_id, orderer, cart):
    payment_method = PaymentMethod.bank_transfer

    order = order_service.place_order(shop_id, orderer, payment_method, cart)

    order_email_service.send_email_for_incoming_order_to_orderer(order.id)

    order_placed.send(None, order_id=order.id)

    return order


def _flash_order_success(order):
    flash_success(
        'Deine Bestellung mit der '
        f'Bestellnummer <strong>{order.order_number}</strong> '
        'wurde entgegen genommen. Vielen Dank!',
        text_is_safe=True,
    )
