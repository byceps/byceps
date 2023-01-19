"""
byceps.services.site_navigation.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import NewType
from uuid import UUID

from ..site.models import SiteID


NavMenuID = NewType('NavMenuID', UUID)


NavItemID = NewType('NavItemID', UUID)


NavItemTargetType = Enum('NavItemTargetType', ['endpoint', 'page', 'url'])


@dataclass(frozen=True)
class NavMenu:
    id: NavMenuID
    site_id: SiteID
    name: str
    language_code: str
    hidden: bool


@dataclass(frozen=True)
class NavItem:
    id: NavItemID
    menu_id: NavMenuID
    position: int
    target_type: NavItemTargetType
    target: str
    label: str
    current_page_id: str
    hidden: bool


@dataclass(frozen=True)
class NavItemForRendering:
    target: str
    label: str
    current_page_id: str
    children: list[NavItemForRendering]


@dataclass(frozen=True)
class NavMenuAggregate(NavMenu):
    items: list[NavItem]
