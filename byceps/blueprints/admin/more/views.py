"""
byceps.blueprints.admin.more.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from ....services.brand import brand_service
from ....services.party import service as party_service
from ....services.site import service as site_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated
from ....util.views import permission_required


blueprint = create_blueprint('more_admin', __name__)


@blueprint.get('/global')
@permission_required('admin.access')
@templated
def view_global():
    """Show more global admin items."""
    return {}


@blueprint.get('/brands/<brand_id>')
@permission_required('admin.access')
@templated
def view_brand(brand_id):
    """Show more brand admin items."""
    brand = brand_service.find_brand(brand_id)
    if brand is None:
        abort(404)

    return {'brand': brand}


@blueprint.get('/parties/<party_id>')
@permission_required('admin.access')
@templated
def view_party(party_id):
    """Show more party admin items."""
    party = party_service.find_party(party_id)
    if party is None:
        abort(404)

    return {'party': party}


@blueprint.get('/sites/<site_id>')
@permission_required('admin.access')
@templated
def view_site(site_id):
    """Show more site admin items."""
    site = site_service.find_site(site_id)
    if site is None:
        abort(404)

    return {'site': site}
