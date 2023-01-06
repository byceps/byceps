"""
byceps.services.site_navigation.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import NewType
from uuid import UUID

from ...site.transfer.models import SiteID


MenuID = NewType('MenuID', UUID)


ItemID = NewType('ItemID', UUID)


ItemTargetType = Enum('ItemTargetType', ['endpoint', 'page', 'url'])


@dataclass(frozen=True)
class Menu:
    id: MenuID
    site_id: SiteID
    name: str
    language_code: str
    hidden: bool


@dataclass(frozen=True)
class Item:
    id: ItemID
    menu_id: MenuID
    position: int
    target_type: ItemTargetType
    target: str
    label: str
    current_page_id: str
    hidden: bool


@dataclass(frozen=True)
class ItemForRendering:
    target: str
    label: str
    current_page_id: str
    children: list[ItemForRendering]


@dataclass(frozen=True)
class MenuAggregate(Menu):
    items: list[Item]
