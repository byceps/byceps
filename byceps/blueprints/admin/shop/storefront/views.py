"""
byceps.blueprints.admin.shop.storefront.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from .....services.brand import service as brand_service
from .....services.shop.catalog import service as catalog_service
from .....services.shop.order import sequence_service as order_sequence_service
from .....services.shop.shop import service as shop_service
from .....services.shop.shop.transfer.models import Shop, ShopID
from .....services.shop.storefront import service as storefront_service
from .....services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to

from .forms import StorefrontCreateForm, StorefrontUpdateForm


blueprint = create_blueprint('shop_storefront_admin', __name__)


@blueprint.get('/for_shop/<shop_id>')
@permission_required('shop.view')
@templated
def index_for_shop(shop_id):
    """List storefronts for that shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    storefronts = storefront_service.get_storefronts_for_shop(shop.id)

    order_number_prefixes_by_sequence_id = (
        _get_order_number_prefixes_by_sequence_id(shop.id)
    )

    return {
        'shop': shop,
        'brand': brand,
        'storefronts': storefronts,
        'order_number_prefixes_by_sequence_id': order_number_prefixes_by_sequence_id,
    }


def _get_order_number_prefixes_by_sequence_id(shop_id):
    sequences = order_sequence_service.get_order_number_sequences_for_shop(
        shop_id
    )
    return {seq.id: seq.prefix for seq in sequences}


@blueprint.get('/<storefront_id>')
@permission_required('shop.view')
@templated
def view(storefront_id):
    """Show a single storefront."""
    storefront = _get_storefront_or_404(storefront_id)

    shop = shop_service.get_shop(storefront.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    order_number_sequence = order_sequence_service.get_order_number_sequence(
        storefront.order_number_sequence_id
    )
    order_number_prefix = order_number_sequence.prefix

    return {
        'storefront': storefront,
        'shop': shop,
        'brand': brand,
        'order_number_prefix': order_number_prefix,
    }


@blueprint.get('/for_shop/<shop_id>/create')
@permission_required('shop.create')
@templated
def create_form(shop_id, erroneous_form=None):
    """Show form to create a storefront."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    catalogs = catalog_service.get_catalogs_for_shop(shop.id)
    order_number_sequences = (
        order_sequence_service.get_order_number_sequences_for_shop(shop.id)
    )
    order_number_sequence_available = bool(order_number_sequences)

    form = erroneous_form if erroneous_form else StorefrontCreateForm()
    form.set_catalog_choices(catalogs)
    form.set_order_number_sequence_choices(order_number_sequences)

    return {
        'shop': shop,
        'brand': brand,
        'order_number_sequence_available': order_number_sequence_available,
        'form': form,
    }


@blueprint.post('/for_shop/<shop_id>')
@permission_required('shop.create')
def create(shop_id):
    """Create a storefront."""
    shop = _get_shop_or_404(shop_id)

    form = StorefrontCreateForm(request.form)

    catalogs = catalog_service.get_catalogs_for_shop(shop.id)

    order_number_sequences = (
        order_sequence_service.get_order_number_sequences_for_shop(shop.id)
    )
    if not order_number_sequences:
        flash_error(
            gettext('No order number sequences are defined for this shop.')
        )
        return create_form(shop_id, form)

    form.set_catalog_choices(catalogs)
    form.set_order_number_sequence_choices(order_number_sequences)
    if not form.validate():
        return create_form(shop_id, form)

    storefront_id = form.id.data.strip()
    catalog_id = form.catalog_id.data or None
    order_number_sequence_id = form.order_number_sequence_id.data

    if not order_number_sequence_id:
        flash_error(gettext('No valid order number sequence was specified.'))
        return create_form(shop_id, form)

    order_number_sequence = order_sequence_service.get_order_number_sequence(
        order_number_sequence_id
    )
    if order_number_sequence.shop_id != shop.id:
        flash_error(gettext('No valid order number sequence was specified.'))
        return create_form(shop_id, form)

    try:
        item_number = order_sequence_service.generate_order_number(
            order_number_sequence.id
        )
    except order_sequence_service.OrderNumberGenerationFailed as e:
        abort(500, e.message)

    storefront = storefront_service.create_storefront(
        storefront_id,
        shop.id,
        order_number_sequence.id,
        closed=False,
        catalog_id=catalog_id,
    )

    flash_success(
        gettext(
            'Storefront "%(storefront_id)s" has been created.',
            storefront_id=storefront.id,
        )
    )
    return redirect_to('.view', storefront_id=storefront.id)


@blueprint.get('/<storefront_id>/update')
@permission_required('shop.update')
@templated
def update_form(storefront_id, erroneous_form=None):
    """Show form to update a storefront."""
    storefront = _get_storefront_or_404(storefront_id)

    shop = shop_service.get_shop(storefront.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    catalogs = catalog_service.get_catalogs_for_shop(storefront.shop_id)
    order_number_sequences = (
        order_sequence_service.get_order_number_sequences_for_shop(shop.id)
    )

    form = (
        erroneous_form
        if erroneous_form
        else StorefrontUpdateForm(obj=storefront)
    )
    form.set_catalog_choices(catalogs)
    form.set_order_number_sequence_choices(order_number_sequences)

    return {
        'storefront': storefront,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<storefront_id>')
@permission_required('shop.update')
def update(storefront_id):
    """Update a storefront."""
    storefront = _get_storefront_or_404(storefront_id)

    catalogs = catalog_service.get_catalogs_for_shop(storefront.shop_id)
    order_number_sequences = (
        order_sequence_service.get_order_number_sequences_for_shop(
            storefront.shop_id
        )
    )

    form = StorefrontUpdateForm(request.form)
    form.set_catalog_choices(catalogs)
    form.set_order_number_sequence_choices(order_number_sequences)
    if not form.validate():
        return update_form(storefront_id, form)

    order_number_sequence_id = form.order_number_sequence_id.data
    catalog_id = form.catalog_id.data or None
    closed = form.closed.data

    storefront = storefront_service.update_storefront(
        storefront.id, catalog_id, order_number_sequence_id, closed
    )

    flash_success(
        gettext(
            'Storefront "%(storefront_id)s" has been updated.',
            storefront_id=storefront.id,
        )
    )
    return redirect_to('.view', storefront_id=storefront.id)


def _get_shop_or_404(shop_id: ShopID) -> Shop:
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop


def _get_storefront_or_404(storefront_id: StorefrontID) -> Storefront:
    storefront = storefront_service.find_storefront(storefront_id)

    if storefront is None:
        abort(404)

    return storefront
