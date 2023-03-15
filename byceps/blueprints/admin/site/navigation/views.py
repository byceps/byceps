"""
byceps.blueprints.admin.site.navigation.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from flask import abort, request
from flask_babel import gettext

from .....services.brand import brand_service
from .....services.page import page_service
from .....services.site.models import Site, SiteID
from .....services.site import site_service
from .....services.site_navigation.models import (
    NavItem,
    NavItemID,
    NavItemTargetType,
    NavMenu,
    NavMenuAggregate,
    NavMenuID,
)
from .....services.site_navigation import site_navigation_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to, respond_no_content

from .forms import (
    ItemCreateEndpointForm,
    ItemCreatePageForm,
    ItemCreateUrlForm,
    ItemUpdateForm,
    MenuCreateForm,
    MenuUpdateForm,
)


blueprint = create_blueprint('site_navigation_admin', __name__)


@blueprint.get('/for_site/<site_id>')
@permission_required('site.view')
@templated
def index_for_site(site_id):
    """List menus for that site."""
    site = _get_site_or_404(site_id)

    brand = brand_service.get_brand(site.brand_id)

    menus = site_navigation_service.get_menus(site.id)

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

    menu = site_navigation_service.create_menu(
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

    menu = site_navigation_service.update_menu(
        menu.id, name, language_code, hidden
    )

    flash_success(gettext('Menu "%(name)s" has been updated.', name=menu.name))

    return redirect_to('.view', menu_id=menu.id)


@blueprint.get('/for_menu/<menu_id>/create/for_endpoint')
@permission_required('site_navigation.administrate')
@templated
def item_create_endpoint_form(menu_id, erroneous_form=None):
    """Show form to create a menu item referencing an endpoint."""
    menu = _get_menu_or_404(menu_id)

    site = site_service.get_site(menu.site_id)
    brand = brand_service.get_brand(site.brand_id)

    form = erroneous_form if erroneous_form else ItemCreateEndpointForm()

    return {
        'menu': menu,
        'site': site,
        'brand': brand,
        'form': form,
        'target_type_name': NavItemTargetType.endpoint.name,
    }


@blueprint.get('/for_menu/<menu_id>/create/for_page')
@permission_required('site_navigation.administrate')
@templated
def item_create_page_form(menu_id, erroneous_form=None):
    """Show form to create a menu item referencing a page."""
    menu = _get_menu_or_404(menu_id)

    site = site_service.get_site(menu.site_id)
    brand = brand_service.get_brand(site.brand_id)

    form = erroneous_form if erroneous_form else ItemCreatePageForm()
    form.set_page_choices(site.id, menu.language_code)

    return {
        'menu': menu,
        'site': site,
        'brand': brand,
        'form': form,
        'target_type_name': NavItemTargetType.page.name,
    }


@blueprint.get('/for_menu/<menu_id>/create/for_url')
@permission_required('site_navigation.administrate')
@templated
def item_create_url_form(menu_id, erroneous_form=None):
    """Show form to create a menu item referencing a URL."""
    menu = _get_menu_or_404(menu_id)

    site = site_service.get_site(menu.site_id)
    brand = brand_service.get_brand(site.brand_id)

    form = erroneous_form if erroneous_form else ItemCreateUrlForm()

    return {
        'menu': menu,
        'site': site,
        'brand': brand,
        'form': form,
        'target_type_name': NavItemTargetType.url.name,
    }


@blueprint.post('/for_menu/<menu_id>/<target_type_name>')
@permission_required('site_navigation.administrate')
def item_create(menu_id, target_type_name):
    """Create a menu item."""
    menu = _get_menu_or_404(menu_id)

    try:
        target_type = NavItemTargetType[target_type_name]
    except KeyError:
        abort(400, f'Unknown target type "{target_type_name}"')

    if target_type == NavItemTargetType.endpoint:
        form = ItemCreateEndpointForm(request.form)
    elif target_type == NavItemTargetType.page:
        form = ItemCreatePageForm(request.form)
        form.set_page_choices(menu.site_id, menu.language_code)
    elif target_type == NavItemTargetType.url:
        form = ItemCreateUrlForm(request.form)

    if not form.validate():
        if target_type == NavItemTargetType.endpoint:
            form_view = item_create_endpoint_form
        elif target_type == NavItemTargetType.page:
            form_view = item_create_page_form
        elif target_type == NavItemTargetType.url:
            form_view = item_create_url_form

        return form_view(menu.id, form)

    if target_type == NavItemTargetType.endpoint:
        target = form.target_endpoint.data.strip()
        current_page_id = form.current_page_id.data.strip()
    elif target_type == NavItemTargetType.page:
        page = page_service.get_page(form.target_page_id.data)
        target = page.name
        current_page_id = form.current_page_id.data.strip()
    elif target_type == NavItemTargetType.url:
        target = form.target_url.data.strip()
        current_page_id = form.current_page_id.data.strip()

    label = form.label.data.strip()
    hidden = form.hidden.data

    item = site_navigation_service.create_item(
        menu.id, target_type, target, label, current_page_id, hidden=hidden
    )

    flash_success(
        gettext('Menu item "%(label)s" has been created.', label=item.label)
    )

    return redirect_to('.view', menu_id=menu.id)


@blueprint.get('/items/<uuid:item_id>/update')
@permission_required('site_navigation.administrate')
@templated
def item_update_form(item_id, erroneous_form=None):
    """Show form to update the menu item."""
    item = _get_item_or_404(item_id)

    menu = site_navigation_service.get_menu(item.menu_id)
    site = site_service.get_site(menu.site_id)
    brand = brand_service.get_brand(site.brand_id)

    data = dataclasses.asdict(item)
    data['target_type'] = item.target_type.name
    form = erroneous_form if erroneous_form else ItemUpdateForm(data=data)

    return {
        'item': item,
        'menu': menu,
        'site': site,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/items/<uuid:item_id>')
@permission_required('site_navigation.administrate')
def item_update(item_id):
    """Update the menu item."""
    item = _get_item_or_404(item_id)

    form = ItemUpdateForm(request.form)
    if not form.validate():
        return item_update_form(item.id, form)

    label = form.label.data.strip()
    target_type = NavItemTargetType[form.target_type.data]
    target = form.target.data.strip()
    current_page_id = form.current_page_id.data.strip()
    hidden = form.hidden.data

    item = site_navigation_service.update_item(
        item.id, target_type, target, label, current_page_id, hidden
    )

    flash_success(
        gettext('Menu item "%(label)s" has been updated.', label=item.label)
    )

    return redirect_to('.view', menu_id=item.menu_id)


@blueprint.post('/items/<uuid:item_id>/up')
@permission_required('site_navigation.administrate')
@respond_no_content
def item_move_up(item_id):
    """Move the menu item upwards by one position."""
    item = _get_item_or_404(item_id)

    try:
        site_navigation_service.move_item_up(item.id)
    except ValueError:
        flash_error(
            gettext(
                'Item "%(label)s" is already at the top.',
                label=item.label,
            )
        )
    else:
        flash_success(
            gettext(
                'Item "%(label)s" has been moved upwards by one position.',
                label=item.label,
            )
        )


@blueprint.post('/items/<uuid:item_id>/down')
@permission_required('site_navigation.administrate')
@respond_no_content
def item_move_down(item_id):
    """Move the menu item downwards by one position."""
    item = _get_item_or_404(item_id)

    try:
        site_navigation_service.move_item_down(item.id)
    except ValueError:
        flash_error(
            gettext(
                'Item "%(label)s" is already at the bottom.',
                label=item.label,
            )
        )
    else:
        flash_success(
            gettext(
                'Item "%(label)s" has been moved downwards by one position.',
                label=item.label,
            )
        )


@blueprint.delete('/items/<uuid:item_id>')
@permission_required('site_navigation.administrate')
@respond_no_content
def item_delete(item_id):
    """Remove the menu item."""
    item = _get_item_or_404(item_id)

    label = item.label

    site_navigation_service.delete_item(item.id)

    flash_success(gettext('Item "%(label)s" has been deleted.', label=label))


def _get_site_or_404(site_id: SiteID) -> Site:
    site = site_service.find_site(site_id)

    if site is None:
        abort(404)

    return site


def _get_menu_or_404(menu_id: NavMenuID) -> NavMenu:
    menu = site_navigation_service.find_menu(menu_id)

    if menu is None:
        abort(404)

    return menu


def _get_menu_aggregate_or_404(menu_id: NavMenuID) -> NavMenuAggregate:
    menu = site_navigation_service.find_menu_aggregate(menu_id)

    if menu is None:
        abort(404)

    return menu


def _get_item_or_404(item_id: NavItemID) -> NavItem:
    item = site_navigation_service.find_item(item_id)

    if item is None:
        abort(404)

    return item
