"""
byceps.blueprints.admin.shop.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext
from moneyed import get_currency

from .....services.brand import brand_service
from .....services.shop.cancelation_request import cancelation_request_service
from .....services.shop.order import (
    order_log_service,
    order_payment_service,
    order_service,
)
from .....services.shop.order.models.log import OrderLogEntryData
from .....services.shop.order.models.order import PaymentState
from .....services.shop.shop import shop_service
from .....services.shop.shop.models import ShopID
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_success
from .....util.framework.templating import templated
from .....util.l10n import get_default_locale, get_locale_str
from .....util.views import permission_required, redirect_to

from ..order.service import enrich_log_entry_data

from .forms import CreateForm


blueprint = create_blueprint('shop_shop_admin', __name__)


@blueprint.get('/shops/<shop_id>/dashboard')
@permission_required('shop.view')
@templated
def dashboard(shop_id):
    """Show the shop dashboard."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    order_counts_by_payment_state = (
        order_service.count_orders_per_payment_state(shop.id)
    )

    cancelation_request_quantities_by_state = (
        cancelation_request_service.get_request_quantities_by_state(shop.id)
    )

    log_entries = _get_latest_log_entries(shop.id)

    return {
        'shop': shop,
        'brand': brand,
        'order_counts_by_payment_state': order_counts_by_payment_state,
        'cancelation_request_quantities_by_state': cancelation_request_quantities_by_state,
        'PaymentState': PaymentState,
        'log_entries': log_entries,
        'render_order_payment_method': order_service.find_payment_method_label,
    }


_LATEST_LOG_ENTRIES_EVENT_TYPES = frozenset(
    [
        'order-canceled-after-paid',
        'order-canceled-before-paid',
        'order-note-added',
        'order-paid',
        'order-placed',
        'order-placed-confirmation-email-resent',
    ]
)


def _get_latest_log_entries(
    shop_id: ShopID, limit=8
) -> list[OrderLogEntryData]:
    log_entries = order_log_service.get_latest_entries_for_shop(
        shop_id, _LATEST_LOG_ENTRIES_EVENT_TYPES, limit
    )
    return list(enrich_log_entry_data(log_entries))


@blueprint.get('/for_shop/<shop_id>')
@permission_required('shop.view')
@templated
def view(shop_id):
    """Show the shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    order_counts_by_payment_state = (
        order_service.count_orders_per_payment_state(shop.id)
    )

    return {
        'shop': shop,
        'brand': brand,
        'order_counts_by_payment_state': order_counts_by_payment_state,
        'PaymentState': PaymentState,
        'settings': shop.extra_settings,
    }


@blueprint.get('/for_brand/<brand_id>')
@permission_required('shop.view')
@templated
def view_for_brand(brand_id):
    brand = _get_brand_or_404(brand_id)

    shop = shop_service.find_shop_for_brand(brand.id)
    if shop is not None:
        return redirect_to('.dashboard', shop_id=shop.id)

    return {
        'brand': brand,
    }


@blueprint.get('/for_brand/<brand_id>/create')
@permission_required('shop.create')
@templated
def create_form(brand_id, erroneous_form=None):
    """Show form to create a shop."""
    brand = _get_brand_or_404(brand_id)

    locale = get_locale_str() or get_default_locale()

    form = erroneous_form if erroneous_form else CreateForm()
    form.set_currency_choices(locale)

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.post('/for_brand/<brand_id>')
@permission_required('shop.create')
def create(brand_id):
    """Create a shop."""
    brand = _get_brand_or_404(brand_id)

    locale = get_default_locale()

    form = CreateForm(request.form)
    form.set_currency_choices(locale)

    if not form.validate():
        return create_form(brand.id, form)

    shop_id = brand.id
    title = brand.title
    currency = get_currency(form.currency.data)

    shop = shop_service.create_shop(shop_id, brand.id, title, currency)

    order_payment_service.create_email_payment_instructions(shop.id, g.user.id)
    order_payment_service.create_html_payment_instructions(shop.id, g.user.id)

    flash_success(gettext('Shop has been created.'))

    return redirect_to('.view', shop_id=shop.id)


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
