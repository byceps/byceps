"""
byceps.services.shop.catalog.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from flask import abort, request
from flask_babel import gettext

from byceps.services.brand import brand_service
from byceps.services.shop.catalog import catalog_service
from byceps.services.shop.catalog.errors import CollectionNotEmptyError
from byceps.services.shop.catalog.models import (
    Catalog,
    CatalogID,
    Collection,
    CollectionID,
)
from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import ProductID
from byceps.services.shop.shop import shop_service
from byceps.services.shop.shop.models import Shop, ShopID
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.result import Err, Ok
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
)

from .forms import (
    CatalogCreateForm,
    CatalogUpdateForm,
    CollectionCreateForm,
    CollectionUpdateForm,
    ProductAddForm,
)


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

    collections_and_products = (
        catalog_service.get_collections_and_products_for_catalog(
            catalog.id,
            only_currently_available=False,
            only_directly_orderable=False,
            only_not_requiring_separate_order=False,
        )
    )

    return {
        'catalog': catalog,
        'shop': shop,
        'brand': brand,
        'collections_and_products': collections_and_products,
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


# collection


@blueprint.get('/catalogs/<catalog_id>/collections/create')
@permission_required('shop_product.administrate')
@templated
def collection_create_form(catalog_id, erroneous_form=None):
    """Show form to create a collection."""
    catalog = _get_catalog_or_404(catalog_id)

    shop = _get_shop_or_404(catalog.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = erroneous_form if erroneous_form else CollectionCreateForm()

    return {
        'catalog': catalog,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/catalogs/<catalog_id>/collections')
@permission_required('shop_product.administrate')
def collection_create(catalog_id):
    """Create a collection."""
    catalog = _get_catalog_or_404(catalog_id)

    form = CollectionCreateForm(request.form)
    if not form.validate():
        return collection_create_form(catalog_id, form)

    title = form.title.data.strip()

    collection = catalog_service.create_collection(catalog.id, title)

    flash_success(
        gettext(
            'Collection "%(title)s" has been created.', title=collection.title
        )
    )

    return redirect_to('.catalog_view', catalog_id=collection.catalog_id)


@blueprint.get('/collections/<collection_id>/update')
@permission_required('shop_product.administrate')
@templated
def collection_update_form(collection_id, erroneous_form=None):
    """Show form to update a collection."""
    collection = _get_collection_or_404(collection_id)

    catalog = catalog_service.get_catalog(collection.catalog_id)
    shop = shop_service.get_shop(catalog.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = (
        erroneous_form
        if erroneous_form
        else CollectionUpdateForm(obj=collection)
    )

    return {
        'collection': collection,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/collections/<collection_id>')
@permission_required('shop_product.administrate')
def collection_update(collection_id):
    """Update a collection."""
    collection = _get_collection_or_404(collection_id)

    form = CollectionUpdateForm(request.form)
    if not form.validate():
        return collection_update_form(collection_id, form)

    title = form.title.data.strip()

    updated_collection = catalog_service.update_collection(collection, title)

    flash_success(
        gettext(
            'Collection "%(title)s" has been updated.',
            title=updated_collection.title,
        )
    )

    return redirect_to(
        '.catalog_view', catalog_id=updated_collection.catalog_id
    )


@blueprint.delete('/collections/<collection_id>')
@permission_required('shop_product.administrate')
@respond_no_content
def collection_delete(collection_id):
    """Delete a collection."""
    collection = _get_collection_or_404(collection_id)

    match catalog_service.delete_collection(collection):
        case Ok(_):
            flash_success(
                gettext(
                    'Collection "%(title)s" has been deleted.',
                    title=collection.title,
                )
            )
        case Err(CollectionNotEmptyError()):
            flash_error(
                gettext(
                    'Collection "%(title)s" cannot be deleted as it contains products.',
                    title=collection.title,
                )
            )
        case Err(_):
            flash_error(gettext('An unexpected error occurred.'))


# product assignment


@blueprint.get('/collections/<collection_id>/products/create')
@permission_required('shop_product.administrate')
@templated
def product_add_form(collection_id, erroneous_form=None):
    """Show form to add a product to a collection."""
    collection = _get_collection_or_404(collection_id)

    catalog = catalog_service.get_catalog(collection.catalog_id)
    shop = _get_shop_or_404(catalog.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = erroneous_form if erroneous_form else ProductAddForm()
    form.set_product_id_choices(collection, shop.id)

    return {
        'collection': collection,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/collections/<collection_id>/products')
@permission_required('shop_product.administrate')
def product_add(collection_id):
    """Add a product to a collection."""
    collection = _get_collection_or_404(collection_id)

    catalog = catalog_service.get_catalog(collection.catalog_id)

    form = ProductAddForm(request.form)
    form.set_product_id_choices(collection, catalog.shop_id)

    if not form.validate():
        return product_add_form(catalog.id, form)

    product_id = ProductID(UUID(form.product_id.data))

    product = product_service.get_product(product_id)

    catalog_service.add_product_to_collection(product.id, collection.id)

    flash_success(
        gettext(
            'Product "%(product_name)s" has been added to collection "%(collection_title)s".',
            product_name=product.name,
            collection_title=collection.title,
        )
    )

    return redirect_to('.catalog_view', catalog_id=collection.catalog_id)


@blueprint.delete('/collections/<collection_id>/products/<product_id>')
@permission_required('shop_product.administrate')
@respond_no_content
def product_remove(collection_id, product_id):
    """Remove a product from a collection."""
    collection = _get_collection_or_404(collection_id)

    product = product_service.get_product(product_id)
    if not product:
        abort(404)

    catalog_service.remove_product_from_collection(product_id, collection_id)

    flash_success(
        gettext(
            'Product "%(product_name)s" has been removed from collection "%(collection_title)s".',
            product_name=product.name,
            collection_title=collection.title,
        )
    )


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


def _get_collection_or_404(collection_id: CollectionID) -> Collection:
    collection = catalog_service.find_collection(collection_id)

    if collection is None:
        abort(404)

    return collection
