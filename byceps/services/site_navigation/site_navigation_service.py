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

from ..site.models import SiteID

from .dbmodels import DbNavItem, DbNavMenu
from .models import (
    NavItem,
    NavItemID,
    NavItemTargetType,
    NavMenu,
    NavMenuAggregate,
    NavMenuID,
    ViewType,
    _VIEW_TYPES,
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
) -> NavMenu:
    """Update a menu."""
    db_menu = _get_db_menu(menu_id)

    db_menu.name = name
    db_menu.language_code = language_code
    db_menu.hidden = hidden

    db.session.commit()

    return _db_entity_to_menu(db_menu)


def create_item(
    menu_id: NavMenuID,
    target_type: NavItemTargetType,
    target: str,
    label: str,
    current_page_id: str,
    *,
    parent_item_id: Optional[NavItemID] = None,
    hidden: bool = False,
) -> NavItem:
    """Create a menu item."""
    db_menu = _get_db_menu(menu_id)

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

    return _db_entity_to_item(db_item)


def update_item(
    item_id: NavItemID,
    target_type: NavItemTargetType,
    target: str,
    label: str,
    current_page_id: str,
    hidden: bool,
) -> NavItem:
    """Update a menu item."""
    db_item = _get_db_item(item_id)

    db_item.target_type = target_type
    db_item.target = target
    db_item.label = label
    db_item.current_page_id = current_page_id
    db_item.hidden = hidden

    db.session.commit()

    return _db_entity_to_item(db_item)


def delete_item(item_id: NavItemID) -> None:
    """Delete a menu item."""
    db_item = _get_db_item(item_id)

    db.session.execute(delete(DbNavItem).where(DbNavItem.id == db_item.id))
    db.session.commit()


def find_menu(menu_id: NavMenuID) -> Optional[NavMenu]:
    """Return the menu, or `None` if not found."""
    db_menu = _find_db_menu(menu_id)

    if db_menu is None:
        return None

    return _db_entity_to_menu(db_menu)


def get_menu(menu_id: NavMenuID) -> NavMenu:
    """Return the menu.

    Raise error if not found.
    """
    db_menu = _get_db_menu(menu_id)

    return _db_entity_to_menu(db_menu)


def _find_db_menu(menu_id: NavMenuID) -> Optional[DbNavMenu]:
    """Return the menu, or `None` if not found."""
    return db.session.get(DbNavMenu, menu_id)


def _get_db_menu(menu_id: NavMenuID) -> DbNavMenu:
    """Return the menu.

    Raise error if not found.
    """
    db_menu = _find_db_menu(menu_id)

    if db_menu is None:
        raise ValueError('Unknown menu ID')

    return db_menu


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


def find_item(item_id: NavItemID) -> Optional[NavItem]:
    """Return the menu item, or `None` if not found."""
    db_item = _find_db_item(item_id)

    if db_item is None:
        return None

    return _db_entity_to_item(db_item)


def _find_db_item(item_id: NavItemID) -> Optional[DbNavItem]:
    """Return the menu item, or `None` if not found."""
    return db.session.get(DbNavItem, item_id)


def _get_db_item(item_id: NavItemID) -> DbNavItem:
    """Return the menu item.

    Raise error if not found.
    """
    db_item = _find_db_item(item_id)

    if db_item is None:
        raise ValueError('Unknown item ID')

    return db_item


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


def move_item_up(item_id: NavItemID) -> NavItem:
    """Move a menu item upwards by one position."""
    item = _get_db_item(item_id)

    item_list = item.menu.items

    if item.position == 1:
        raise ValueError('Item is already at the top.')

    item_index = index_of(item_list, lambda x: x.id == item.id)
    popped_item = item_list.pop(item_index)
    item_list.insert(popped_item.position - 2, popped_item)

    db.session.commit()

    return _db_entity_to_item(item)


def move_item_down(item_id: NavItemID) -> NavItem:
    """Move a menu item downwards by one position."""
    item = _get_db_item(item_id)

    item_list = item.menu.items

    if item.position == len(item_list):
        raise ValueError('Item is already at the bottom.')

    item_index = index_of(item_list, lambda x: x.id == item.id)
    popped_item = item_list.pop(item_index)
    item_list.insert(popped_item.position, popped_item)

    db.session.commit()

    return _db_entity_to_item(item)


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
