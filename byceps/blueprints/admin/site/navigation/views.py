"""
byceps.blueprints.admin.site.navigation.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from flask_babel import gettext

from .....services.brand import brand_service
from .....services.site import site_service
from .....services.site.transfer.models import Site, SiteID
from .....services.site_navigation import service as navigation_service
from .....services.site_navigation.transfer.models import (
    ItemTargetType,
    Menu,
    MenuAggregate,
    MenuID,
)
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to

from .forms import ItemCreateForm, MenuCreateForm, MenuUpdateForm


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


@blueprint.get('/menus/<menu_id>/update')
@permission_required('site_navigation.administrate')
@templated
def menu_update_form(menu_id, erroneous_form=None):
    """Show form to update the menu."""
    menu = _get_menu_or_404(menu_id)

    site = site_service.get_site(menu.site_id)
    brand = brand_service.get_brand(site.brand_id)

    form = erroneous_form if erroneous_form else MenuUpdateForm(obj=menu)

    return {
        'menu': menu,
        'site': site,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/menus/<menu_id>')
@permission_required('site_navigation.administrate')
def menu_update(menu_id):
    """Update the menu."""
    menu = _get_menu_or_404(menu_id)

    form = MenuUpdateForm(request.form)
    if not form.validate():
        return menu_update_form(menu.id, form)

    name = form.name.data.strip()
    language_code = form.language_code.data.strip()
    hidden = form.hidden.data

    menu = navigation_service.update_menu(menu.id, name, language_code, hidden)

    flash_success(gettext('Menu "%(name)s" has been updated.', name=menu.name))

    return redirect_to('.view', menu_id=menu.id)


@blueprint.get('/for_menu/<menu_id>/create')
@permission_required('site_navigation.administrate')
@templated
def item_create_form(menu_id, erroneous_form=None):
    """Show form to create a menu item."""
    menu = _get_menu_or_404(menu_id)

    site = site_service.get_site(menu.site_id)
    brand = brand_service.get_brand(site.brand_id)

    form = erroneous_form if erroneous_form else ItemCreateForm()

    return {
        'menu': menu,
        'site': site,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/for_menu/<menu_id>/create')
@permission_required('site_navigation.administrate')
def item_create(menu_id):
    """Create a menu item."""
    menu = _get_menu_or_404(menu_id)

    form = ItemCreateForm(request.form)
    if not form.validate():
        return item_create_form(menu.id, form)

    target_type = ItemTargetType[form.target_type.data]
    target = form.target.data.strip()
    label = form.label.data.strip()
    current_page_id = form.current_page_id.data.strip()
    hidden = form.hidden.data

    item = navigation_service.create_item(
        menu.id, target_type, target, label, current_page_id, hidden=hidden
    )

    flash_success(
        gettext('Menu item "%(label)s" has been created.', label=item.label)
    )

    return redirect_to('.view', menu_id=menu.id)


def _get_site_or_404(site_id: SiteID) -> Site:
    site = site_service.find_site(site_id)

    if site is None:
        abort(404)

    return site


def _get_menu_or_404(menu_id: MenuID) -> Menu:
    menu = navigation_service.find_menu(menu_id)

    if menu is None:
        abort(404)

    return menu


def _get_menu_aggregate_or_404(menu_id: MenuID) -> MenuAggregate:
    menu = navigation_service.find_menu_aggregate(menu_id)

    if menu is None:
        abort(404)

    return menu
