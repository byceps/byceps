"""
byceps.blueprints.admin.shop.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from flask import abort, url_for
from flask_babel import gettext

from .....services.brand import brand_service
from .....services.shop.order import order_log_service, order_service
from .....services.shop.order.transfer.log import OrderLogEntryData
from .....services.shop.order.transfer.order import PaymentState
from .....services.shop.shop import shop_service
from .....services.shop.shop.transfer.models import ShopID
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_success
from .....util.framework.templating import templated
from .....util.views import (
    permission_required,
    redirect_to,
    respond_no_content_with_location,
)

from ..order.service import enrich_log_entry_data


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

    log_entries = _get_latest_log_entries(shop.id)

    return {
        'shop': shop,
        'brand': brand,
        'order_counts_by_payment_state': order_counts_by_payment_state,
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
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    shop = shop_service.find_shop_for_brand(brand.id)
    if shop is not None:
        return redirect_to('.dashboard', shop_id=shop.id)

    return {
        'brand': brand,
    }


@blueprint.post('/for_brand/<brand_id>')
@permission_required('shop.create')
@respond_no_content_with_location
def create(brand_id):
    """Create a shop."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    shop_id = brand.id
    title = brand.title

    shop = shop_service.create_shop(shop_id, brand.id, title)

    flash_success(gettext('Shop has been created.'))
    return url_for('.view', shop_id=shop.id)


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
