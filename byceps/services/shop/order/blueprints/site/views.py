"""
byceps.services.shop.order.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from flask import abort, g, request
from flask_babel import gettext, format_percent
from moneyed import Currency

from byceps.services.country import country_service
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.catalog import catalog_service
from byceps.services.shop.order import (
    order_checkout_service,
    order_service,
    signals as shop_order_signals,
)
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.product import product_domain_service, product_service
from byceps.services.shop.product.errors import NoProductsAvailableError
from byceps.services.shop.product.models import (
    Product,
    ProductCollection,
    ProductCompilation,
    ProductCompilationBuilder,
)
from byceps.services.shop.shop import shop_service
from byceps.services.shop.storefront import storefront_service
from byceps.services.site.blueprints.site.navigation import (
    subnavigation_for_view,
)
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_notice, flash_success
from byceps.util.framework.templating import templated
from byceps.util.result import Err, Ok, Result
from byceps.util.views import login_required, redirect_to

from .forms import assemble_products_order_form, OrderForm


blueprint = create_blueprint('shop_order', __name__)


@blueprint.add_app_template_filter
def tax_rate_as_percentage(tax_rate) -> str:
    # Keep a digit after the decimal point in case
    # the tax rate is a fractional number.
    return format_percent(tax_rate, '#0.0 %')


@blueprint.get('/order')
@templated
@subnavigation_for_view('shop')
def order_form(erroneous_form=None):
    """Show a form to order products."""
    storefront = _get_storefront_or_404()
    shop = shop_service.get_shop(storefront.shop_id)

    if storefront.closed:
        flash_notice(gettext('The shop is closed.'))
        return {'collections': None}

    if storefront.catalog:
        collections = catalog_service.get_product_collections_for_catalog(
            storefront.catalog.id, include_unavailable_products=False
        )
    else:
        compilation_result = (
            product_service.get_product_compilation_for_orderable_products(
                shop.id
            )
        )

        match compilation_result:
            case Err(e):
                if isinstance(e, NoProductsAvailableError):
                    error_message = gettext('No products are available.')
                else:
                    error_message = gettext('An unknown error has occurred.')

                flash_error(error_message)
                return {'collections': None}

        compilation = compilation_result.unwrap()

        collection = (
            product_service.get_product_collection_for_product_compilation(
                '', compilation
            )
        )
        collections = [collection]

    products = _get_products_from_collections(collections)

    product_ids = {product.id for product in products}
    if not product_ids:
        error_message = gettext('No products are available.')
        flash_error(error_message)
        return {'collections': None}

    images_by_product_id = product_service.get_images_for_products(product_ids)

    if not g.user.authenticated:
        return list_products(collections)

    detail = user_service.get_detail(g.user.id)

    if erroneous_form:
        form = erroneous_form
    else:
        product_compilation = _build_product_compilation(products)
        ProductsOrderForm = assemble_products_order_form(product_compilation)
        form = ProductsOrderForm(obj=detail)

    country_names = country_service.get_country_names()

    return {
        'form': form,
        'country_names': country_names,
        'collections': collections,
        'images_by_product_id': images_by_product_id,
    }


# No route registered. Intended to be called from another view function.
@templated
@subnavigation_for_view('shop')
def list_products(collections: list[ProductCollection]):
    """List products for anonymous users to view."""
    return {
        'collections': collections,
    }


@blueprint.post('/order')
@login_required
def order():
    """Order products."""
    storefront = _get_storefront_or_404()
    shop = shop_service.get_shop(storefront.shop_id)

    if storefront.closed:
        flash_notice(gettext('The shop is closed.'))
        return order_form()

    if storefront.catalog:
        collections = catalog_service.get_product_collections_for_catalog(
            storefront.catalog.id, include_unavailable_products=False
        )
    else:
        compilation_result = (
            product_service.get_product_compilation_for_orderable_products(
                shop.id
            )
        )

        match compilation_result:
            case Err(e):
                if isinstance(e, NoProductsAvailableError):
                    error_message = gettext('No products are available.')
                else:
                    error_message = gettext('An unknown error has occurred.')

                flash_error(error_message)
                return order_form()

        compilation = compilation_result.unwrap()

        collection = (
            product_service.get_product_collection_for_product_compilation(
                '', compilation
            )
        )
        collections = [collection]

    products = _get_products_from_collections(collections)

    product_ids = {product.id for product in products}
    if not product_ids:
        error_message = gettext('No products are available.')
        flash_error(error_message)
        return order_form()

    product_compilation = _build_product_compilation(products)

    ProductsOrderForm = assemble_products_order_form(product_compilation)
    form = ProductsOrderForm(request.form)

    if not form.validate():
        return order_form(form)

    cart = form.get_cart(product_compilation)

    if cart.is_empty():
        flash_error(gettext('No products have been selected.'))
        return order_form(form)

    orderer = form.get_orderer(g.user)

    placement_result = _place_order(storefront, orderer, cart)
    if placement_result.is_err():
        flash_error(gettext('Placing the order has failed.'))
        return order_form(form)

    order = placement_result.unwrap()

    _flash_order_success(order)

    return redirect_to('shop_orders.view', order_id=order.id)


@blueprint.get('/order_single/<uuid:product_id>')
@login_required
@templated
@subnavigation_for_view('shop')
def order_single_form(product_id, erroneous_form=None):
    """Show a form to order a single product."""
    product = _get_product_or_404(product_id)

    storefront = _get_storefront_or_404()
    shop = shop_service.get_shop(storefront.shop_id)

    user = g.user
    detail = user_service.get_detail(user.id)

    form = erroneous_form if erroneous_form else OrderForm(obj=detail)

    if storefront.closed:
        flash_notice(gettext('The shop is closed.'))
        return {
            'form': form,
            'product': None,
        }

    compilation = product_service.get_product_compilation_for_single_product(
        product.id
    )

    collection = product_service.get_product_collection_for_product_compilation(
        '', compilation
    )
    collections = [collection]

    country_names = country_service.get_country_names()

    if product.not_directly_orderable:
        flash_error(gettext('The product cannot be ordered directly.'))
        return {
            'form': form,
            'product': None,
        }

    if order_service.has_user_placed_orders(user.id, shop.id):
        flash_error(gettext('You cannot place another order.'))
        return {
            'form': form,
            'product': None,
        }

    if (
        product.quantity < 1
        or not product_domain_service.is_product_available_now(product)
    ):
        flash_error(gettext('The product is not available.'))
        return {
            'form': form,
            'product': None,
        }

    images_by_product_id = product_service.get_images_for_products({product.id})

    return {
        'form': form,
        'country_names': country_names,
        'product': product,
        'collections': collections,
        'images_by_product_id': images_by_product_id,
    }


@blueprint.post('/order_single/<uuid:product_id>')
@login_required
def order_single(product_id):
    """Order a single product."""
    product = _get_product_or_404(product_id)

    storefront = _get_storefront_or_404()
    shop = shop_service.get_shop(storefront.shop_id)

    if storefront.closed:
        flash_notice(gettext('The shop is closed.'))
        return order_single_form(product.id)

    if product.not_directly_orderable:
        flash_error(gettext('The product cannot be ordered directly.'))
        return order_single_form(product.id)

    compilation = product_service.get_product_compilation_for_single_product(
        product.id
    )

    user = g.user

    if order_service.has_user_placed_orders(user.id, shop.id):
        flash_error(gettext('You cannot place another order.'))
        return order_single_form(product.id)

    if (
        product.quantity < 1
        or not product_domain_service.is_product_available_now(product)
    ):
        flash_error(gettext('The product is not available.'))
        return order_single_form(product.id)

    form = OrderForm(request.form)
    if not form.validate():
        return order_single_form(product.id, form)

    orderer = form.get_orderer(user)

    cart = _create_cart_from_product_compilation(shop.currency, compilation)

    placement_result = _place_order(storefront, orderer, cart)
    if placement_result.is_err():
        flash_error(gettext('Placing the order has failed.'))
        return order_form(form)

    order = placement_result.unwrap()

    _flash_order_success(order)

    return redirect_to('shop_orders.view', order_id=order.id)


def _get_storefront_or_404():
    storefront_id = g.site.storefront_id
    if storefront_id is None:
        abort(404)

    return storefront_service.get_storefront(storefront_id)


def _get_product_or_404(product_id):
    product = product_service.find_db_product(product_id)

    if product is None:
        abort(404)

    return product


def _get_products_from_collections(
    collections: list[ProductCollection],
) -> list[Product]:
    return [
        item.product for collection in collections for item in collection.items
    ]


def _build_product_compilation(
    products: Iterable[Product],
) -> ProductCompilation:
    builder = ProductCompilationBuilder()

    for product in products:
        builder.append_product(product)

    return builder.build()


def _create_cart_from_product_compilation(
    currency: Currency, compilation: ProductCompilation
) -> Cart:
    cart = Cart(currency)

    for item in compilation:
        cart.add_item(item.product, item.fixed_quantity)

    return cart


def _place_order(storefront, orderer, cart) -> Result[Order, None]:
    placement_result = order_checkout_service.place_order(
        storefront, orderer, cart
    )
    if placement_result.is_err():
        return Err(None)

    order, event = placement_result.unwrap()

    order_email_service.send_email_for_incoming_order_to_orderer(order)

    shop_order_signals.order_placed.send(None, event=event)

    return Ok(order)


def _flash_order_success(order):
    flash_success(
        gettext(
            'Your order <strong>%(order_number)s</strong> has been placed. '
            'Thank you!',
            order_number=order.order_number,
        ),
        text_is_safe=True,
    )
