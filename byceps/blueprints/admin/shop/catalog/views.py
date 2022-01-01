"""
byceps.blueprints.admin.shop.catalog.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from .....services.brand import service as brand_service
from .....services.shop.catalog import service as catalog_service
from .....services.shop.catalog.transfer.models import Catalog, CatalogID
from .....services.shop.shop import service as shop_service
from .....services.shop.shop.transfer.models import Shop, ShopID
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated
from .....util.views import permission_required


blueprint = create_blueprint('shop_catalog_admin', __name__)


@blueprint.get('/for_shop/<shop_id>')
@permission_required('shop.view')
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


@blueprint.get('/<catalog_id>')
@permission_required('shop.view')
@templated
def view(catalog_id):
    """Show a single catalog."""
    catalog = _get_catalog_or_404(catalog_id)

    shop = shop_service.get_shop(catalog.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    return {
        'catalog': catalog,
        'shop': shop,
        'brand': brand,
    }


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
