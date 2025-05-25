"""
byceps.services.shop.catalog.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from byceps.services.brand import brand_service
from byceps.services.shop.catalog import catalog_service
from byceps.services.shop.catalog.models import Catalog, CatalogID
from byceps.services.shop.shop import shop_service
from byceps.services.shop.shop.models import Shop, ShopID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, redirect_to

from .forms import CatalogCreateForm, CatalogUpdateForm


blueprint = create_blueprint('shop_catalog_admin', __name__)


# catalog


@blueprint.get('/for_shop/<shop_id>')
@permission_required('shop_product.view')
@templated
def index_for_shop(shop_id):
    """List catalogs for that shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    catalogs = catalog_service.get_catalogs_for_shop(shop.id)

    return {
        'shop': shop,
        'brand': brand,
        'catalogs': catalogs,
    }


@blueprint.get('/catalogs/<catalog_id>')
@permission_required('shop_product.view')
@templated
def catalog_view(catalog_id):
    """Show a single catalog."""
    catalog = _get_catalog_or_404(catalog_id)

    shop = shop_service.get_shop(catalog.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    collections = catalog_service.get_product_collections_for_catalog(
        catalog.id, include_unavailable_products=True
    )

    return {
        'catalog': catalog,
        'shop': shop,
        'brand': brand,
        'collections': collections,
    }


@blueprint.get('/for_shop/<shop_id>/create')
@permission_required('shop_product.administrate')
@templated
def catalog_create_form(shop_id, erroneous_form=None):
    """Show form to create a catalog."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    form = erroneous_form if erroneous_form else CatalogCreateForm()

    return {
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/for_shop/<shop_id>')
@permission_required('shop_product.administrate')
def catalog_create(shop_id):
    """Create a catalog."""
    shop = _get_shop_or_404(shop_id)

    form = CatalogCreateForm(request.form)
    if not form.validate():
        return catalog_create_form(shop_id, form)

    title = form.title.data.strip()

    catalog = catalog_service.create_catalog(shop.id, title)

    flash_success(
        gettext('Catalog "%(title)s" has been created.', title=catalog.title)
    )
    return redirect_to('.catalog_view', catalog_id=catalog.id)


@blueprint.get('/catalogs/<catalog_id>/update')
@permission_required('shop_product.administrate')
@templated
def catalog_update_form(catalog_id, erroneous_form=None):
    """Show form to update a catalog."""
    catalog = _get_catalog_or_404(catalog_id)

    shop = shop_service.get_shop(catalog.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    form = erroneous_form if erroneous_form else CatalogUpdateForm(obj=catalog)

    return {
        'catalog': catalog,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/catalogs/<catalog_id>')
@permission_required('shop_product.administrate')
def catalog_update(catalog_id):
    """Update a catalog."""
    catalog = _get_catalog_or_404(catalog_id)

    form = CatalogUpdateForm(request.form)
    if not form.validate():
        return catalog_update_form(catalog_id, form)

    title = form.title.data.strip()

    updated_catalog = catalog_service.update_catalog(catalog, title)

    flash_success(
        gettext(
            'Catalog "%(title)s" has been updated.', title=updated_catalog.title
        )
    )
    return redirect_to('.catalog_view', catalog_id=updated_catalog.id)


# helpers


def _get_shop_or_404(shop_id: ShopID) -> Shop:
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop


def _get_catalog_or_404(catalog_id: CatalogID) -> Catalog:
    catalog = catalog_service.find_catalog(catalog_id)

    if catalog is None:
        abort(404)

    return catalog
