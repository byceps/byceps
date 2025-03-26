"""
byceps.services.more.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from byceps.services.brand import brand_service
from byceps.services.party import party_service
from byceps.services.site import site_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required

from . import item_service


blueprint = create_blueprint('more_admin', __name__)


@blueprint.get('/global')
@permission_required('admin.access')
@templated
def view_global():
    """Show more global admin items."""
    return {
        'items': item_service.select_visible_items(
            item_service.get_global_items()
        ),
    }


@blueprint.get('/brands/<brand_id>')
@permission_required('admin.access')
@templated
def view_brand(brand_id):
    """Show more brand admin items."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    return {
        'brand': brand,
        'items': item_service.select_visible_items(
            item_service.get_brand_items(brand)
        ),
    }


@blueprint.get('/parties/<party_id>')
@permission_required('admin.access')
@templated
def view_party(party_id):
    """Show more party admin items."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    return {
        'party': party,
        'items': item_service.select_visible_items(
            item_service.get_party_items(party)
        ),
    }


@blueprint.get('/sites/<site_id>')
@permission_required('admin.access')
@templated
def view_site(site_id):
    """Show more site admin items."""
    site = site_service.find_site(site_id)
    if site is None:
        abort(404)

    return {
        'site': site,
        'items': item_service.select_visible_items(
            item_service.get_site_items(site)
        ),
    }
