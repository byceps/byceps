"""
byceps.services.site_navigation.site_navigation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterable, Optional

from sqlalchemy import delete, select

from ...database import db
from ...util.iterables import find, index_of
from ...util.result import Err, Ok, Result

from ..site.models import SiteID

from .dbmodels import DbNavItem, DbNavMenu
from .models import (
    _VIEW_TYPES,
    NavItem,
    NavItemID,
    NavItemTargetType,
    NavMenu,
    NavMenuAggregate,
    NavMenuID,
    NavMenuTree,
    ViewType,
)


def create_menu(
    site_id: SiteID,
    name: str,
    language_code: str,
    *,
    hidden: bool = False,
    parent_menu_id: Optional[NavMenuID] = None,
) -> NavMenu:
    """Create a menu."""
    db_menu = DbNavMenu(
        site_id, name, language_code, hidden, parent_menu_id=parent_menu_id
    )
    db.session.add(db_menu)
    db.session.commit()

    return _db_entity_to_menu(db_menu)


def update_menu(
    menu_id: NavMenuID,
    name: str,
    language_code: str,
    hidden: bool,
) -> Result[NavMenu, str]:
    """Update a menu."""

    def _update_menu(db_menu: DbNavMenu) -> DbNavMenu:
        db_menu.name = name
        db_menu.language_code = language_code
        db_menu.hidden = hidden

        db.session.commit()

        return db_menu

    return _get_db_menu(menu_id).map(_update_menu).map(_db_entity_to_menu)


def create_item(
    menu_id: NavMenuID,
    target_type: NavItemTargetType,
    target: str,
    label: str,
    current_page_id: str,
    *,
    parent_item_id: Optional[NavItemID] = None,
    hidden: bool = False,
) -> Result[NavItem, str]:
    """Create a menu item."""

    def _create_item(db_menu: DbNavMenu) -> DbNavMenu:
        db_item = DbNavItem(
            db_menu.id,
            parent_item_id,
            target_type,
            target,
            label,
            current_page_id,
            hidden,
        )
        db_menu.items.append(db_item)
        db.session.commit()

        return db_item

    return _get_db_menu(menu_id).map(_create_item).map(_db_entity_to_item)


def update_item(
    item_id: NavItemID,
    target_type: NavItemTargetType,
    target: str,
    label: str,
    current_page_id: str,
    hidden: bool,
) -> Result[NavItem, str]:
    """Update a menu item."""

    def _update_item(db_item: DbNavItem) -> DbNavItem:
        db_item.target_type = target_type
        db_item.target = target
        db_item.label = label
        db_item.current_page_id = current_page_id
        db_item.hidden = hidden

        db.session.commit()

        return db_item

    return _get_db_item(item_id).map(_update_item).map(_db_entity_to_item)


def delete_item(item_id: NavItemID) -> Result[None, str]:
    """Delete a menu item."""

    def _delete_item(db_item: DbNavItem) -> None:
        db.session.execute(delete(DbNavItem).where(DbNavItem.id == db_item.id))
        db.session.commit()

    return _get_db_item(item_id).map(_delete_item)


def find_submenu_id_for_page(
    site_id: SiteID, language_code: str, page_name: str
) -> Optional[NavMenuID]:
    """Return the ID of the submenu this page is referenced by.

    If the page is referenced from multiple submenus, the one whose name
    comes first in alphabetical order is chosen.
    """
    return db.session.scalars(
        select(DbNavItem.menu_id)
        .join(DbNavMenu)
        .filter(DbNavMenu.site_id == site_id)
        .filter(DbNavMenu.language_code == language_code)
        .filter(DbNavMenu.hidden == False)  # noqa: E712
        .filter(DbNavMenu.parent_menu_id.is_not(None))  # submenus only
        .filter(DbNavItem._target_type == NavItemTargetType.page.name)
        .filter(DbNavItem.target == page_name)
        .filter(DbNavItem.hidden == False)  # noqa: E712
        .order_by(DbNavMenu.name)
    ).first()


def find_submenu_id_for_view(
    site_id: SiteID, language_code: str, view_name: str
) -> Optional[NavMenuID]:
    """Return the ID of the submenu this view is referenced by.

    If the view is referenced from multiple submenus, the one whose name
    comes first in alphabetical order is chosen.
    """
    return db.session.scalars(
        select(DbNavItem.menu_id)
        .join(DbNavMenu)
        .filter(DbNavMenu.site_id == site_id)
        .filter(DbNavMenu.language_code == language_code)
        .filter(DbNavMenu.hidden == False)  # noqa: E712
        .filter(DbNavMenu.parent_menu_id.is_not(None))  # submenus only
        .filter(DbNavItem._target_type == NavItemTargetType.view.name)
        .filter(DbNavItem.target == view_name)
        .filter(DbNavItem.hidden == False)  # noqa: E712
        .order_by(DbNavMenu.name)
    ).first()


def find_menu(menu_id: NavMenuID) -> Optional[NavMenu]:
    """Return the menu, or `None` if not found."""
    db_menu = _find_db_menu(menu_id)

    if db_menu is None:
        return None

    return _db_entity_to_menu(db_menu)


def get_menu(menu_id: NavMenuID) -> Result[NavMenu, str]:
    """Return the menu.

    Return error if not found.
    """
    return _get_db_menu(menu_id).map(_db_entity_to_menu)


def _find_db_menu(menu_id: NavMenuID) -> Optional[DbNavMenu]:
    """Return the menu, or `None` if not found."""
    return db.session.get(DbNavMenu, menu_id)


def _get_db_menu(menu_id: NavMenuID) -> Result[DbNavMenu, str]:
    """Return the menu.

    Return error if not found.
    """
    db_menu = _find_db_menu(menu_id)

    if db_menu is None:
        return Err('Unknown menu ID')

    return Ok(db_menu)


def find_menu_aggregate(menu_id: NavMenuID) -> Optional[NavMenuAggregate]:
    """Return the menu aggregate, or `None` if not found."""
    db_menu = _find_db_menu(menu_id)
    if db_menu is None:
        return None

    db_items = db.session.scalars(
        select(DbNavItem).filter(DbNavItem.menu_id == db_menu.id)
    )

    return _db_entity_to_menu_aggregate(db_menu, db_items)


def get_menus(site_id: SiteID) -> list[NavMenu]:
    """Return the menus for this site."""
    db_menus = db.session.scalars(
        select(DbNavMenu).filter(DbNavMenu.site_id == site_id)
    )

    return [_db_entity_to_menu(db_menu) for db_menu in db_menus]


def get_menu_trees(site_id: SiteID) -> list[NavMenuTree]:
    """Return the menu trees for this site."""
    menus = get_menus(site_id)

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


def find_item(item_id: NavItemID) -> Optional[NavItem]:
    """Return the menu item, or `None` if not found."""
    db_item = _find_db_item(item_id)

    if db_item is None:
        return None

    return _db_entity_to_item(db_item)


def _find_db_item(item_id: NavItemID) -> Optional[DbNavItem]:
    """Return the menu item, or `None` if not found."""
    return db.session.get(DbNavItem, item_id)


def _get_db_item(item_id: NavItemID) -> Result[DbNavItem, str]:
    """Return the menu item.

    Return error if not found.
    """
    db_item = _find_db_item(item_id)

    if db_item is None:
        return Err('Unknown item ID')

    return Ok(db_item)


def get_items_for_menu_id(menu_id: NavMenuID) -> list[NavItem]:
    """Return the items of a menu.

    An empty list is returned if the menu does not exist, is hidden, or
    contains no visible items.
    """
    db_items = db.session.scalars(
        select(DbNavItem)
        .join(DbNavMenu)
        .filter(DbNavMenu.id == menu_id)
        .filter(DbNavMenu.hidden == False)  # noqa: E712
        .filter(DbNavItem.hidden == False)  # noqa: E712
    )

    return _db_entities_to_items(db_items)


def get_items_for_menu(
    site_id: SiteID, name: str, language_code: str
) -> list[NavItem]:
    """Return the items of a menu.

    An empty list is returned if the menu does not exist, is hidden, or
    contains no visible items.
    """
    db_items = db.session.scalars(
        select(DbNavItem)
        .join(DbNavMenu)
        .filter(DbNavMenu.site_id == site_id)
        .filter(DbNavMenu.name == name)
        .filter(DbNavMenu.language_code == language_code)
        .filter(DbNavMenu.hidden == False)  # noqa: E712
        .filter(DbNavItem.hidden == False)  # noqa: E712
    )

    return _db_entities_to_items(db_items)


def move_item_up(item_id: NavItemID) -> Result[NavItem, str]:
    """Move a menu item upwards by one position."""

    def _move_item_up(db_item: DbNavItem) -> Result[DbNavItem, str]:
        if db_item.position == 1:
            return Err('Item is already at the top.')

        item_list = db_item.menu.items
        item_index = index_of(item_list, lambda x: x.id == db_item.id)
        popped_item = item_list.pop(item_index)
        item_list.insert(popped_item.position - 2, popped_item)

        db.session.commit()

        return Ok(db_item)

    return _get_db_item(item_id).and_then(_move_item_up).map(_db_entity_to_item)


def move_item_down(item_id: NavItemID) -> Result[NavItem, str]:
    """Move a menu item downwards by one position."""

    def _move_item_down(db_item: DbNavItem) -> Result[DbNavItem, str]:
        item_list = db_item.menu.items

        if db_item.position == len(item_list):
            return Err('Item is already at the bottom.')

        item_index = index_of(item_list, lambda x: x.id == db_item.id)
        popped_item = item_list.pop(item_index)
        item_list.insert(popped_item.position, popped_item)

        db.session.commit()

        return Ok(db_item)

    return (
        _get_db_item(item_id).and_then(_move_item_down).map(_db_entity_to_item)
    )


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


def _db_entity_to_menu_aggregate(
    db_menu: DbNavMenu, db_items: Iterable[DbNavItem]
) -> NavMenuAggregate:
    menu = _db_entity_to_menu(db_menu)
    items = _db_entities_to_items(db_items)

    return NavMenuAggregate(
        id=menu.id,
        site_id=menu.site_id,
        name=menu.name,
        language_code=menu.language_code,
        hidden=menu.hidden,
        parent_menu_id=menu.parent_menu_id,
        items=items,
    )


def get_view_types() -> list[ViewType]:
    """Return the available view types."""
    return list(_VIEW_TYPES)


def find_view_type_by_name(name: str) -> Optional[ViewType]:
    """Return the view type with that name, or `None` if not found."""
    return find(_VIEW_TYPES, lambda view_type: view_type.name == name)
