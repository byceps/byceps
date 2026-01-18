"""
byceps.services.site_navigation.site_navigation_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from byceps.services.site.models import SiteID
from byceps.util.uuid import generate_uuid7

from .models import NavItem, NavItemID, NavItemTargetType, NavMenu, NavMenuID


# -------------------------------------------------------------------- #
# menu


def create_menu(
    site_id: SiteID,
    name: str,
    language_code: str,
    hidden: bool,
    parent_menu_id: NavMenuID | None,
) -> NavMenu:
    """Create a menu."""
    menu_id = NavMenuID(generate_uuid7())

    return NavMenu(
        id=menu_id,
        site_id=site_id,
        name=name,
        language_code=language_code,
        hidden=hidden,
        parent_menu_id=parent_menu_id,
    )


def update_menu(
    menu: NavMenu,
    name: str,
    language_code: str,
    hidden: bool,
) -> NavMenu:
    """Update a menu."""
    return dataclasses.replace(
        menu,
        name=name,
        language_code=language_code,
        hidden=hidden,
    )


# -------------------------------------------------------------------- #
# item


def create_item(
    menu_id: NavMenuID,
    target_type: NavItemTargetType,
    target: str,
    label: str,
    current_page_id: str,
    hidden: bool,
) -> NavItem:
    """Create a menu item."""
    item_id = NavItemID(generate_uuid7())

    return NavItem(
        id=item_id,
        menu_id=menu_id,
        position=0,
        target_type=target_type,
        target=target,
        label=label,
        current_page_id=current_page_id,
        hidden=hidden,
    )


def update_item(
    item: NavItem,
    target_type: NavItemTargetType,
    target: str,
    label: str,
    current_page_id: str,
    hidden: bool,
) -> NavItem:
    """Update a menu item."""
    return dataclasses.replace(
        item,
        target_type=target_type,
        target=target,
        label=label,
        current_page_id=current_page_id,
        hidden=hidden,
    )
