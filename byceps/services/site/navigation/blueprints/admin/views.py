"""
byceps.services.site.navigation.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from flask import abort, request
from flask_babel import gettext

from byceps.services.brand import brand_service
from byceps.services.page import page_service
from byceps.services.site import site_service
from byceps.services.site.models import Site, SiteID
from byceps.services.site_navigation import (
    site_navigation_service,
    view_type_registry,
)
from byceps.services.site_navigation.models import (
    NavItem,
    NavItemID,
    NavItemTargetType,
    NavMenu,
    NavMenuID,
)
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
    ItemCreatePageForm,
    ItemCreateUrlForm,
    ItemCreateViewForm,
    ItemUpdateForm,
    MenuCreateForm,
    MenuTreesCopyForm,
    MenuUpdateForm,
    SubMenuCreateForm,
)


blueprint = create_blueprint('site_navigation_admin', __name__)


@blueprint.get('/for_site/<site_id>')
@permission_required('site.view')
@templated
def index_for_site(site_id):
    """List menus for that site."""
    site = _get_site_or_404(site_id)

    brand = brand_service.get_brand(site.brand_id)

    menu_trees = site_navigation_service.get_menu_trees(site.id)

    return {
        'site': site,
        'brand': brand,
        'menu_trees': menu_trees,
    }


@blueprint.get('/<menu_id>')
@permission_required('site.view')
@templated
def view(menu_id):
    """Show a single menu."""
    menu = _get_menu_or_404(menu_id)

    menu_with_items = site_navigation_service.get_menu_with_unfiltered_items(
        menu
    )

    site = site_service.get_site(menu.site_id)
    brand = brand_service.get_brand(site.brand_id)

    return {
        'menu': menu_with_items,
        'site': site,
        'brand': brand,
    }


@blueprint.get('/for_site/<target_site_id>/copy')
@permission_required('site_navigation.administrate')
@templated
def menu_trees_copy_form(target_site_id, erroneous_form=None):
    """Show form to copy menu trees from another site."""
    target_site = _get_site_or_404(target_site_id)

    form = erroneous_form if erroneous_form else MenuTreesCopyForm()
    form.set_source_site_id_choices(target_site)

    return {
        'form': form,
        'target_site': target_site,
    }


@blueprint.post('/for_site/<target_site_id>/copy')
@permission_required('site_navigation.administrate')
def menu_trees_copy(target_site_id):
    """Copy menu trees from another site."""
    target_site = _get_site_or_404(target_site_id)

    form = MenuTreesCopyForm(request.form)
    form.set_source_site_id_choices(target_site)

    if not form.validate():
        return redirect_to('.index_for_site', site_id=target_site.id)

    source_site_id = form.source_site_id.data
    source_site = _get_site_or_404(source_site_id)

    match site_navigation_service.copy_site_menu_trees(
        source_site.id, target_site.id
    ):
        case Ok(_):
            flash_success(gettext('Menus have been successfully copied.'))
        case Err(e):
            flash_error(e)

    return redirect_to('.index_for_site', site_id=target_site.id)


@blueprint.get('/for_site/<site_id>/create')
@permission_required('site_navigation.administrate')
@templated
def menu_create_form(site_id, erroneous_form=None):
    """Show form to create a menu."""
    site = _get_site_or_404(site_id)

    brand = brand_service.get_brand(site.brand_id)

    form = erroneous_form if erroneous_form else MenuCreateForm()
    form.set_language_choices()

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
    form.set_language_choices()

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


@blueprint.get('/for_site/<site_id>/create/below/<parent_menu_id>')
@permission_required('site_navigation.administrate')
@templated
def submenu_create_form(site_id, parent_menu_id, erroneous_form=None):
    """Show form to create a submenu."""
    site = _get_site_or_404(site_id)

    brand = brand_service.get_brand(site.brand_id)

    parent_menu = site_navigation_service.get_menu(parent_menu_id).unwrap()

    form = erroneous_form if erroneous_form else SubMenuCreateForm()

    return {
        'site': site,
        'brand': brand,
        'form': form,
        'parent_menu': parent_menu,
    }


@blueprint.post('/for_site/<site_id>/below/<parent_menu_id>')
@permission_required('site_navigation.administrate')
def submenu_create(site_id, parent_menu_id):
    """Create a submenu."""
    site = _get_site_or_404(site_id)

    parent_menu = site_navigation_service.get_menu(parent_menu_id).unwrap()

    form = SubMenuCreateForm(request.form)

    if not form.validate():
        return submenu_create_form(site_id, parent_menu_id, form)

    name = form.name.data.strip()
    hidden = form.hidden.data

    menu = site_navigation_service.create_menu(
        site.id,
        name,
        parent_menu.language_code,
        hidden=hidden,
        parent_menu_id=parent_menu_id,
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
    form.set_language_choices()

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
    form.set_language_choices()
    if not form.validate():
        return menu_update_form(menu.id, form)

    name = form.name.data.strip()
    language_code = form.language_code.data.strip()
    hidden = form.hidden.data

    menu = site_navigation_service.update_menu(
        menu, name, language_code, hidden
    ).unwrap()

    flash_success(gettext('Menu "%(name)s" has been updated.', name=menu.name))

    return redirect_to('.view', menu_id=menu.id)


@blueprint.get('/for_menu/<menu_id>/create/for_page')
@permission_required('site_navigation.administrate')
@templated
def item_create_page_form(menu_id, erroneous_form=None):
    """Show form to create a menu item referencing a page."""
    menu = _get_menu_or_404(menu_id)

    site = site_service.get_site(menu.site_id)
    brand = brand_service.get_brand(site.brand_id)

    form = erroneous_form if erroneous_form else ItemCreatePageForm()
    form.set_page_choices(site.id)

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


@blueprint.get('/for_menu/<menu_id>/create/for_view')
@permission_required('site_navigation.administrate')
@templated
def item_create_view_form(menu_id, erroneous_form=None):
    """Show form to create a menu item referencing a view."""
    menu = _get_menu_or_404(menu_id)

    site = site_service.get_site(menu.site_id)
    brand = brand_service.get_brand(site.brand_id)

    form = erroneous_form if erroneous_form else ItemCreateViewForm()
    form.set_view_type_choices()

    return {
        'menu': menu,
        'site': site,
        'brand': brand,
        'form': form,
        'target_type_name': NavItemTargetType.view.name,
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

    form = _get_create_form(target_type, request, menu)

    if not form.validate():
        form_view = _get_create_form_view(target_type)
        return form_view(menu.id, form)

    target, current_page_id = _get_target_and_current_page_id_for_create_form(
        target_type, form
    )

    label = form.label.data.strip()
    hidden = form.hidden.data

    item = site_navigation_service.create_item(
        menu.id, target_type, target, label, current_page_id, hidden=hidden
    ).unwrap()

    flash_success(
        gettext('Menu item "%(label)s" has been created.', label=item.label)
    )

    return redirect_to('.view', menu_id=menu.id)


def _get_create_form(target_type: NavItemTargetType, request, menu: NavMenu):
    match target_type:
        case NavItemTargetType.page:
            form = ItemCreatePageForm(request.form)
            form.set_page_choices(menu.site_id)

        case NavItemTargetType.url:
            form = ItemCreateUrlForm(request.form)

        case NavItemTargetType.view:
            form = ItemCreateViewForm(request.form)
            form.set_view_type_choices()

    return form


def _get_create_form_view(target_type: NavItemTargetType):
    match target_type:
        case NavItemTargetType.page:
            return item_create_page_form

        case NavItemTargetType.url:
            return item_create_url_form

        case NavItemTargetType.view:
            return item_create_view_form


def _get_target_and_current_page_id_for_create_form(
    target_type: NavItemTargetType, form
) -> tuple[str, str]:
    match target_type:
        case NavItemTargetType.page:
            page = page_service.get_page(form.target_page_id.data)
            target = page.name
            current_page_id = page.current_page_id

        case NavItemTargetType.url:
            target = form.target_url.data.strip()
            current_page_id = form.current_page_id.data.strip()

        case NavItemTargetType.view:
            view_type_name = form.target_view_type.data
            view_type = view_type_registry.find_view_type_by_name(
                view_type_name
            )
            if not view_type:
                abort(400, f'Unknown view type "{view_type_name}"')

            target = view_type.name
            current_page_id = view_type.current_page_id

    return target, current_page_id


@blueprint.get('/items/<uuid:item_id>/update')
@permission_required('site_navigation.administrate')
@templated
def item_update_form(item_id, erroneous_form=None):
    """Show form to update the menu item."""
    item = _get_item_or_404(item_id)

    menu = site_navigation_service.get_menu(item.menu_id).unwrap()
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
        item, target_type, target, label, current_page_id, hidden
    ).unwrap()

    flash_success(
        gettext('Menu item "%(label)s" has been updated.', label=item.label)
    )

    return redirect_to('.view', menu_id=item.menu_id)


@blueprint.post('/items/<uuid:item_id>/hide')
@permission_required('site_navigation.administrate')
@respond_no_content
def item_hide(item_id):
    """Hide the menu item."""
    item = _get_item_or_404(item_id)

    item = site_navigation_service.update_item(
        item,
        item.target_type,
        item.target,
        item.label,
        item.current_page_id,
        True,
    ).unwrap()

    flash_success(
        gettext('Menu item "%(label)s" has been hidden.', label=item.label)
    )


@blueprint.post('/items/<uuid:item_id>/unhide')
@permission_required('site_navigation.administrate')
@respond_no_content
def item_unhide(item_id):
    """Un-hide the menu item."""
    item = _get_item_or_404(item_id)

    item = site_navigation_service.update_item(
        item,
        item.target_type,
        item.target,
        item.label,
        item.current_page_id,
        False,
    ).unwrap()

    flash_success(
        gettext(
            'Menu item "%(label)s" has been made visible.', label=item.label
        )
    )


@blueprint.post('/items/<uuid:item_id>/up')
@permission_required('site_navigation.administrate')
@respond_no_content
def item_move_up(item_id):
    """Move the menu item upwards by one position."""
    item = _get_item_or_404(item_id)

    move_result = site_navigation_service.move_item_up(item.id)
    if move_result.is_err():
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

    move_result = site_navigation_service.move_item_down(item.id)
    if move_result.is_err():
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

    site_navigation_service.delete_item(item.id).unwrap()

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


def _get_item_or_404(item_id: NavItemID) -> NavItem:
    item = site_navigation_service.find_item(item_id)

    if item is None:
        abort(404)

    return item
