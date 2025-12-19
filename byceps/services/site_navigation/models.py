"""
byceps.services.site_navigation.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType, Self
from uuid import UUID

from byceps.services.site.models import SiteID


NavMenuID = NewType('NavMenuID', UUID)


NavItemID = NewType('NavItemID', UUID)


NavItemTargetType = Enum(
    'NavItemTargetType', ['endpoint', 'page', 'url', 'view']
)


@dataclass(frozen=True, kw_only=True)
class NavMenu:
    id: NavMenuID
    site_id: SiteID
    name: str
    language_code: str
    hidden: bool
    parent_menu_id: NavMenuID | None


@dataclass(frozen=True, kw_only=True)
class NavItem:
    id: NavItemID
    menu_id: NavMenuID
    position: int
    target_type: NavItemTargetType
    target: str
    label: str
    current_page_id: str
    hidden: bool


@dataclass(frozen=True, kw_only=True)
class NavItemForRendering:
    target: str
    label: str
    current_page_id: str
    children: list[NavItemForRendering]


@dataclass(frozen=True)
class NavMenuWithItems(NavMenu):
    items: list[NavItem]

    @classmethod
    def from_menu_and_items(cls, menu: NavMenu, items: list[NavItem]) -> Self:
        return cls(
            id=menu.id,
            site_id=menu.site_id,
            name=menu.name,
            language_code=menu.language_code,
            hidden=menu.hidden,
            parent_menu_id=menu.parent_menu_id,
            items=items,
        )


@dataclass(frozen=True, kw_only=True)
class NavMenuTree:
    menu: NavMenu
    submenus: list[NavMenu]
