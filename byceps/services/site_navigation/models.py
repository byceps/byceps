"""
byceps.services.site_navigation.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType, Optional
from uuid import UUID

from flask_babel import lazy_gettext

from ..site.models import SiteID


NavMenuID = NewType('NavMenuID', UUID)


NavItemID = NewType('NavItemID', UUID)


NavItemTargetType = Enum(
    'NavItemTargetType', ['endpoint', 'page', 'url', 'view']
)


@dataclass(frozen=True)
class NavMenu:
    id: NavMenuID
    site_id: SiteID
    name: str
    language_code: str
    hidden: bool
    parent_menu_id: Optional[NavMenuID]


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


@dataclass(frozen=True)
class ViewType:
    name: str
    endpoint: str
    label: str
    current_page_id: str


_VIEW_TYPES = [
    ViewType(
        name=name,
        endpoint=endpoint,
        label=label,
        current_page_id=current_page_id,
    )
    for name, endpoint, label, current_page_id in [
        ('news', 'news.index', lazy_gettext('News'), 'news'),
        ('seating_plan', 'seating.index', lazy_gettext('Seating plan'), 'seating'),
        ('attendees', 'attendance.attendees', lazy_gettext('Attendees'), 'attendees'),
        ('shop', 'shop_order.order_form', lazy_gettext('Shop'), 'shop_order'),
        ('board', 'board.category_index', lazy_gettext('Board'), 'board'),
        ('orga_team', 'orga_team.index', lazy_gettext('Orga team'), 'orga_team'),
        ('party_history', 'party_history.index', lazy_gettext('Party history'), 'party_history'),
    ]
]


@dataclass(frozen=True)
class NavMenuTree:
    menu: NavMenu
    submenus: list[NavMenu]
