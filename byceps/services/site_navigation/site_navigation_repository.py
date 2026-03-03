"""
byceps.services.site_navigation.site_navigation_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.site.models import SiteID
from byceps.util.iterables import index_of
from byceps.util.result import Err, Ok, Result

from .dbmodels import DbNavItem, DbNavMenu
from .models import (
    NavItem,
    NavItemID,
    NavItemTargetType,
    NavMenu,
    NavMenuID,
)


def create_menu(menu: NavMenu) -> None:
    """Create a menu."""
    db_menu = DbNavMenu(
        menu.id,
        menu.site_id,
        menu.name,
        menu.language_code,
        menu.hidden,
        parent_menu_id=menu.parent_menu_id,
    )

    db.session.add(db_menu)
    db.session.commit()


def update_menu(menu: NavMenu) -> Result[None, str]:
    """Update a menu."""

    def _update_menu(db_menu: DbNavMenu) -> None:
        db_menu.name = menu.name
        db_menu.language_code = menu.language_code
        db_menu.hidden = menu.hidden

        db.session.commit()

    return _get_db_menu(menu.id).map(_update_menu)


def create_item(item: NavItem) -> Result[None, str]:
    """Create a menu item."""

    def _create_item(db_menu: DbNavMenu) -> None:
        db_item = DbNavItem(
            item.id,
            item.menu_id,
            item.target_type,
            item.target,
            item.label,
            item.current_page_id,
            item.hidden,
        )
        db_menu.items.append(db_item)

        db.session.commit()

    return _get_db_menu(item.menu_id).map(_create_item)


def update_item(item: NavItem) -> Result[None, str]:
    """Update a menu item."""

    def _update_item(db_item: DbNavItem) -> None:
        db_item.target_type = item.target_type
        db_item.target = item.target
        db_item.label = item.label
        db_item.current_page_id = item.current_page_id
        db_item.hidden = item.hidden

        db.session.commit()

    return _get_db_item(item.id).map(_update_item)


def delete_item(item_id: NavItemID) -> Result[None, str]:
    """Delete a menu item."""

    def _delete_item(db_item: DbNavItem) -> None:
        db.session.execute(delete(DbNavItem).where(DbNavItem.id == db_item.id))
        db.session.commit()

    return _get_db_item(item_id).map(_delete_item)


def find_submenu_id_for_page(
    site_id: SiteID, language_code: str, page_name: str
) -> NavMenuID | None:
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
) -> NavMenuID | None:
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


def find_menu(menu_id: NavMenuID) -> DbNavMenu | None:
    """Return the menu, or `None` if not found."""
    return db.session.get(DbNavMenu, menu_id)


def get_menu(menu_id: NavMenuID) -> Result[DbNavMenu, str]:
    """Return the menu.

    Return error if not found.
    """
    return _get_db_menu(menu_id)


def _get_db_menu(menu_id: NavMenuID) -> Result[DbNavMenu, str]:
    """Return the menu.

    Return error if not found.
    """
    db_menu = find_menu(menu_id)

    if db_menu is None:
        return Err('Unknown menu ID')

    return Ok(db_menu)


def get_menus(site_id: SiteID) -> Sequence[DbNavMenu]:
    """Return the menus for this site."""
    return db.session.scalars(
        select(DbNavMenu).filter(DbNavMenu.site_id == site_id)
    ).all()


def find_item(item_id: NavItemID) -> DbNavItem | None:
    """Return the menu item, or `None` if not found."""
    return _find_db_item(item_id)


def _find_db_item(item_id: NavItemID) -> DbNavItem | None:
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


def get_items_for_menu_id_unfiltered(menu_id: NavMenuID) -> Sequence[DbNavItem]:
    """Return the items of a menu.

    An empty list is returned if the menu does not exist.
    """
    return db.session.scalars(
        select(DbNavItem).filter(DbNavItem.menu_id == menu_id)
    ).all()


def get_items_for_menu_id(menu_id: NavMenuID) -> Sequence[DbNavItem]:
    """Return the items of a menu.

    An empty list is returned if the menu does not exist, is hidden, or
    contains no visible items.
    """
    return db.session.scalars(
        select(DbNavItem)
        .join(DbNavMenu)
        .filter(DbNavMenu.id == menu_id)
        .filter(DbNavMenu.hidden == False)  # noqa: E712
        .filter(DbNavItem.hidden == False)  # noqa: E712
    ).all()


def get_items_for_menu(
    site_id: SiteID, name: str, language_code: str
) -> Sequence[DbNavItem]:
    """Return the items of a menu.

    An empty list is returned if the menu does not exist, is hidden, or
    contains no visible items.
    """
    return db.session.scalars(
        select(DbNavItem)
        .join(DbNavMenu)
        .filter(DbNavMenu.site_id == site_id)
        .filter(DbNavMenu.name == name)
        .filter(DbNavMenu.language_code == language_code)
        .filter(DbNavMenu.hidden == False)  # noqa: E712
        .filter(DbNavItem.hidden == False)  # noqa: E712
    ).all()


def move_item_up(item_id: NavItemID) -> Result[None, str]:
    """Move a menu item upwards by one position."""

    def _move_item_up(db_item: DbNavItem) -> Result[None, str]:
        if db_item.position == 1:
            return Err('Item is already at the top.')

        item_list = db_item.menu.items
        item_index = index_of(item_list, lambda x: x.id == db_item.id)
        popped_item = item_list.pop(item_index)
        item_list.insert(popped_item.position - 2, popped_item)

        db.session.commit()

        return Ok(None)

    return _get_db_item(item_id).and_then(_move_item_up)


def move_item_down(item_id: NavItemID) -> Result[None, str]:
    """Move a menu item downwards by one position."""

    def _move_item_down(db_item: DbNavItem) -> Result[None, str]:
        item_list = db_item.menu.items

        if db_item.position == len(item_list):
            return Err('Item is already at the bottom.')

        item_index = index_of(item_list, lambda x: x.id == db_item.id)
        popped_item = item_list.pop(item_index)
        item_list.insert(popped_item.position, popped_item)

        db.session.commit()

        return Ok(None)

    return _get_db_item(item_id).and_then(_move_item_down)
