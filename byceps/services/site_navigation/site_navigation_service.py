"""
byceps.services.site_navigation.site_navigation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterable, Optional

from sqlalchemy import select

from ...database import db
from ...services.site.transfer.models import SiteID

from .dbmodels import DbItem, DbMenu
from .transfer.models import (
    Item,
    ItemID,
    ItemTargetType,
    Menu,
    MenuAggregate,
    MenuID,
)


def create_menu(
    site_id: SiteID,
    name: str,
    language_code: str,
    *,
    hidden: bool = False,
) -> Menu:
    """Create a menu."""
    db_menu = DbMenu(site_id, name, language_code, hidden)
    db.session.add(db_menu)
    db.session.commit()

    return _db_entity_to_menu(db_menu)


def update_menu(
    menu_id: MenuID,
    name: str,
    language_code: str,
    hidden: bool,
) -> Menu:
    """Update a menu."""
    db_menu = _get_db_menu(menu_id)

    db_menu.name = name
    db_menu.language_code = language_code
    db_menu.hidden = hidden

    db.session.commit()

    return _db_entity_to_menu(db_menu)


def create_item(
    menu_id: MenuID,
    target_type: ItemTargetType,
    target: str,
    label: str,
    current_page_id: str,
    *,
    parent_item_id: Optional[ItemID] = None,
    hidden: bool = False,
) -> Item:
    """Create a menu item."""
    db_menu = _get_db_menu(menu_id)

    db_item = DbItem(
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


def find_menu(menu_id: MenuID) -> Optional[Menu]:
    """Return the menu, or `None` if not found."""
    db_menu = _find_db_menu(menu_id)

    if db_menu is None:
        return None

    return _db_entity_to_menu(db_menu)


def get_menu(menu_id: MenuID) -> Menu:
    """Return the menu.

    Raise error if not found.
    """
    db_menu = _get_db_menu(menu_id)

    return _db_entity_to_menu(db_menu)


def _find_db_menu(menu_id: MenuID) -> Optional[DbMenu]:
    """Return the menu, or `None` if not found."""
    return db.session.get(DbMenu, menu_id)


def _get_db_menu(menu_id: MenuID) -> DbMenu:
    """Return the menu.

    Raise error if not found.
    """
    db_menu = _find_db_menu(menu_id)

    if db_menu is None:
        raise ValueError('Unknown menu ID')

    return db_menu


def find_menu_aggregate(menu_id: MenuID) -> Optional[MenuAggregate]:
    """Return the menu aggregate, or `None` if not found."""
    db_menu = _find_db_menu(menu_id)
    if db_menu is None:
        return None

    db_items = db.session.scalars(
        select(DbItem)
        .filter(DbItem.menu_id == db_menu.id)
    )

    return _db_entity_to_menu_aggregate(db_menu, db_items)


def get_menus(site_id: SiteID) -> list[Menu]:
    """Return the menus for this site."""
    db_menus = db.session.scalars(
        select(DbMenu).filter(DbMenu.site_id == site_id)
    )

    return [_db_entity_to_menu(db_menu) for db_menu in db_menus]


def get_items_for_menu(
    site_id: SiteID, name: str, language_code: str
) -> list[Item]:
    """Return the items of a menu.

    An empty list is returned if the menu does not exist, is hidden, or
    contains no visible items.
    """
    db_items = db.session.scalars(
        select(DbItem)
        .join(DbMenu)
        .filter(DbMenu.site_id == site_id)
        .filter(DbMenu.name == name)
        .filter(DbMenu.language_code == language_code)
        .filter(DbMenu.hidden == False)
    )

    return [_db_entity_to_item(db_item) for db_item in db_items]


def _db_entity_to_menu(db_menu: DbMenu) -> Menu:
    return Menu(
        id=db_menu.id,
        site_id=db_menu.site_id,
        name=db_menu.name,
        language_code=db_menu.language_code,
        hidden=db_menu.hidden,
    )


def _db_entity_to_item(db_item: DbItem) -> Item:
    return Item(
        id=db_item.id,
        menu_id=db_item.menu_id,
        position=db_item.position,
        target_type=db_item.target_type,
        target=db_item.target,
        label=db_item.label,
        current_page_id=db_item.current_page_id,
        hidden=db_item.hidden,
    )


def _db_entity_to_menu_aggregate(
    db_menu: DbMenu, db_items: Iterable[DbItem]
) -> MenuAggregate:
    menu = _db_entity_to_menu(db_menu)
    items = [_db_entity_to_item(db_item) for db_item in db_items]

    return MenuAggregate(
        id=menu.id,
        site_id=menu.site_id,
        name=menu.name,
        language_code=menu.language_code,
        hidden=menu.hidden,
        items=items,
    )
