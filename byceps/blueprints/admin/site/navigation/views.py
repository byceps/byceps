"""
byceps.blueprints.admin.site.navigation.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort

from .....services.brand import service as brand_service
from .....services.site import service as site_service
from .....services.site.transfer.models import Site, SiteID
from .....services.site_navigation import service as navigation_service
from .....services.site_navigation.transfer.models import MenuAggregate, MenuID
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated
from .....util.views import permission_required


blueprint = create_blueprint('site_navigation_admin', __name__)


@blueprint.get('/for_site/<site_id>')
@permission_required('site.view')
@templated
def index_for_site(site_id):
    """List menus for that site."""
    site = _get_site_or_404(site_id)

    brand = brand_service.get_brand(site.brand_id)

    menus = navigation_service.get_menus(site.id)

    return {
        'site': site,
        'brand': brand,
        'menus': menus,
    }


@blueprint.get('/<menu_id>')
@permission_required('site.view')
@templated
def view(menu_id):
    """Show a single menu."""
    menu = _get_menu_aggregate_or_404(menu_id)

    site = site_service.get_site(menu.site_id)

    brand = brand_service.get_brand(site.brand_id)

    return {
        'menu': menu,
        'site': site,
        'brand': brand,
    }


def _get_site_or_404(site_id: SiteID) -> Site:
    site = site_service.find_site(site_id)

    if site is None:
        abort(404)

    return site


def _get_menu_aggregate_or_404(menu_id: MenuID) -> MenuAggregate:
    menu = navigation_service.find_menu_aggregate(menu_id)

    if menu is None:
        abort(404)

    return menu
