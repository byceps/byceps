"""
byceps.blueprints.admin.site.navigation.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from .....services.brand import service as brand_service
from .....services.site import service as site_service
from .....services.site.transfer.models import Site, SiteID
from .....services.site_navigation import service as navigation_service
from .....services.site_navigation.transfer.models import MenuAggregate, MenuID
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to

from .forms import MenuCreateForm


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


@blueprint.get('/for_site/<site_id>/create')
@permission_required('site_navigation.administrate')
@templated
def menu_create_form(site_id, erroneous_form=None):
    """Show form to create a menu."""
    site = _get_site_or_404(site_id)

    brand = brand_service.get_brand(site.brand_id)

    form = erroneous_form if erroneous_form else MenuCreateForm()

    return {
        'site': site,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/for_site/<site_id>')
@permission_required('site_navigation.administrate')
def menu_create(site_id):
    """Create a menu."""
    site = _get_site_or_404(site_id)

    form = MenuCreateForm(request.form)

    if not form.validate():
        return menu_create_form(site_id, form)

    name = form.name.data.strip()
    language_code = form.language_code.data.strip()
    hidden = form.hidden.data

    menu = navigation_service.create_menu(
        site.id, name, language_code, hidden=hidden
    )

    flash_success(gettext('Menu "%(name)s" has been created.', name=menu.name))
    return redirect_to('.view', menu_id=menu.id)


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
