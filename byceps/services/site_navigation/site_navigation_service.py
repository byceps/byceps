"""
byceps.services.site_navigation.site_navigation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from byceps.services.site import site_service
from byceps.services.site.models import SiteID
from byceps.util.result import Err, Ok, Result

from . import site_navigation_domain_service, site_navigation_repository
from .dbmodels import DbNavItem, DbNavMenu
from .models import (
    NavItem,
    NavItemID,
    NavItemTargetType,
    NavMenu,
    NavMenuID,
    NavMenuTree,
    NavMenuWithItems,
)


def copy_site_menu_trees(
    source_site_id: SiteID, target_site_id: SiteID
) -> Result[None, str]:
    """Copy all menus and their items from one site to another."""
    if not site_service.find_site(source_site_id):
        return Err('Source site not found.')

    source_menu_trees = get_menu_trees(source_site_id)
    if not source_menu_trees:
        return Err('Source site has no menus that could be copied.')

    if not site_service.find_site(target_site_id):
        return Err('Target site not found.')

    if get_menu_trees(target_site_id):
        return Err('Target site already has menus.')

    for tree in source_menu_trees:
        match copy_menu_tree(tree, target_site_id):
            case Err(e):
                return Err(e)

    return Ok(None)


def copy_menu_tree(
    source_tree: NavMenuTree, target_site_id: SiteID
) -> Result[None, str]:
    """Copy a menu tree's menus and their items from one site to another."""
    match copy_menu_with_items(source_tree.menu, target_site_id):
        case Ok(target_root_menu):
            pass
        case Err(e):
            return Err(e)

    for source_menu in source_tree.submenus:
        match copy_menu_with_items(
            source_menu,
            target_site_id,
            target_parent_menu_id=target_root_menu.id,
        ):
            case Err(e):
                return Err(e)

    return Ok(None)


def copy_menu_with_items(
    source_menu: NavMenuWithItems,
    target_site_id: SiteID,
    *,
    target_parent_menu_id: NavMenuID | None = None,
) -> Result[NavMenu, str]:
    """Copy a menu and its items to another site."""
    target_menu = create_menu(
        target_site_id,
        source_menu.name,
        source_menu.language_code,
        hidden=source_menu.hidden,
        parent_menu_id=target_parent_menu_id,
    )
    match copy_items(source_menu, target_menu.id):
        case Err(e):
            return Err(e)

    return Ok(target_menu)


def create_menu(
    site_id: SiteID,
    name: str,
    language_code: str,
    *,
    hidden: bool = False,
    parent_menu_id: NavMenuID | None = None,
) -> NavMenu:
    """Create a menu."""
    menu = site_navigation_domain_service.create_menu(
        site_id, name, language_code, hidden, parent_menu_id
    )

    site_navigation_repository.create_menu(menu)

    return menu


def update_menu(
    menu: NavMenu,
    name: str,
    language_code: str,
    hidden: bool,
) -> Result[NavMenu, str]:
    """Update a menu."""
    updated_menu = site_navigation_domain_service.update_menu(
        menu, name, language_code, hidden
    )

    return site_navigation_repository.update_menu(updated_menu).map(
        lambda _: updated_menu
    )


def copy_items(
    source_menu: NavMenuWithItems, target_menu_id: NavMenuID
) -> Result[None, str]:
    """Copy a menu's items to another menu."""
    for source_item in source_menu.items:
        match copy_item(source_item, target_menu_id):
            case Err(e):
                return Err(e)

    return Ok(None)


def copy_item(item: NavItem, target_menu_id: NavMenuID) -> Result[NavItem, str]:
    """Copy a menu item to another menu."""
    return create_item(
        target_menu_id,
        item.target_type,
        item.target,
        item.label,
        item.current_page_id,
        hidden=item.hidden,
    )


def create_item(
    menu_id: NavMenuID,
    target_type: NavItemTargetType,
    target: str,
    label: str,
    current_page_id: str,
    *,
    hidden: bool = False,
) -> Result[NavItem, str]:
    """Create a menu item."""
    item = site_navigation_domain_service.create_item(
        menu_id, target_type, target, label, current_page_id, hidden
    )

    return site_navigation_repository.create_item(item).map(lambda _: item)


def update_item(
    item: NavItem,
    target_type: NavItemTargetType,
    target: str,
    label: str,
    current_page_id: str,
    hidden: bool,
) -> Result[NavItem, str]:
    """Update a menu item."""
    updated_item = site_navigation_domain_service.update_item(
        item, target_type, target, label, current_page_id, hidden
    )

    return site_navigation_repository.update_item(updated_item).map(
        lambda _: updated_item
    )


def delete_item(item_id: NavItemID) -> Result[None, str]:
    """Delete a menu item."""
    return site_navigation_repository.delete_item(item_id)


def find_submenu_id_for_page(
    site_id: SiteID, language_code: str, page_name: str
) -> NavMenuID | None:
    """Return the ID of the submenu this page is referenced by.

    If the page is referenced from multiple submenus, the one whose name
    comes first in alphabetical order is chosen.
    """
    return site_navigation_repository.find_submenu_id_for_page(
        site_id, language_code, page_name
    )


def find_submenu_id_for_view(
    site_id: SiteID, language_code: str, view_name: str
) -> NavMenuID | None:
    """Return the ID of the submenu this view is referenced by.

    If the view is referenced from multiple submenus, the one whose name
    comes first in alphabetical order is chosen.
    """
    return site_navigation_repository.find_submenu_id_for_view(
        site_id, language_code, view_name
    )


def find_menu(menu_id: NavMenuID) -> NavMenu | None:
    """Return the menu, or `None` if not found."""
    db_menu = site_navigation_repository.find_menu(menu_id)

    if db_menu is None:
        return None

    return _db_entity_to_menu(db_menu)


def get_menu(menu_id: NavMenuID) -> Result[NavMenu, str]:
    """Return the menu.

    Return error if not found.
    """
    return site_navigation_repository.get_menu(menu_id).map(_db_entity_to_menu)


def get_menu_with_unfiltered_items(menu: NavMenu) -> NavMenuWithItems:
    """Return the menu with items."""
    db_items = site_navigation_repository.get_items_for_menu_id_unfiltered(
        menu.id
    )
    items = _db_entities_to_items(db_items)

    return NavMenuWithItems.from_menu_and_items(menu, items)


def get_menus(site_id: SiteID) -> list[NavMenu]:
    """Return the menus for this site."""
    db_menus = site_navigation_repository.get_menus(site_id)

    return [_db_entity_to_menu(db_menu) for db_menu in db_menus]


def get_menu_trees(site_id: SiteID) -> list[NavMenuTree]:
    """Return the menu trees with items for this site."""
    menus = [
        NavMenuWithItems.from_menu_and_items(
            menu, get_menu_with_unfiltered_items(menu).items
        )
        for menu in get_menus(site_id)
    ]

    trees = []

    root_menus = [menu for menu in menus if not menu.parent_menu_id]
    all_submenus = [menu for menu in menus if menu.parent_menu_id]

    for root_menu in root_menus:
        submenus = [
            menu for menu in all_submenus if menu.parent_menu_id == root_menu.id
        ]
        tree = NavMenuTree(menu=root_menu, submenus=submenus)
        trees.append(tree)

    return trees


def find_item(item_id: NavItemID) -> NavItem | None:
    """Return the menu item, or `None` if not found."""
    db_item = site_navigation_repository.find_item(item_id)

    if db_item is None:
        return None

    return _db_entity_to_item(db_item)


def get_items_for_menu_id(menu_id: NavMenuID) -> list[NavItem]:
    """Return the items of a menu.

    An empty list is returned if the menu does not exist, is hidden, or
    contains no visible items.
    """
    db_items = site_navigation_repository.get_items_for_menu_id(menu_id)

    return _db_entities_to_items(db_items)


def get_items_for_menu(
    site_id: SiteID, name: str, language_code: str
) -> list[NavItem]:
    """Return the items of a menu.

    An empty list is returned if the menu does not exist, is hidden, or
    contains no visible items.
    """
    db_items = site_navigation_repository.get_items_for_menu(
        site_id, name, language_code
    )

    return _db_entities_to_items(db_items)


def move_item_up(item_id: NavItemID) -> Result[None, str]:
    """Move a menu item upwards by one position."""
    return site_navigation_repository.move_item_up(item_id)


def move_item_down(item_id: NavItemID) -> Result[None, str]:
    """Move a menu item downwards by one position."""
    return site_navigation_repository.move_item_down(item_id)


def _db_entity_to_menu(db_menu: DbNavMenu) -> NavMenu:
    return NavMenu(
        id=db_menu.id,
        site_id=db_menu.site_id,
        name=db_menu.name,
        language_code=db_menu.language_code,
        hidden=db_menu.hidden,
        parent_menu_id=db_menu.parent_menu_id,
    )


def _db_entity_to_item(db_item: DbNavItem) -> NavItem:
    return NavItem(
        id=db_item.id,
        menu_id=db_item.menu_id,
        position=db_item.position,
        target_type=db_item.target_type,
        target=db_item.target,
        label=db_item.label,
        current_page_id=db_item.current_page_id,
        hidden=db_item.hidden,
    )


def _db_entities_to_items(db_items: Iterable[DbNavItem]) -> list[NavItem]:
    items = [_db_entity_to_item(db_item) for db_item in db_items]
    items.sort(key=lambda item: item.position)
    return items
