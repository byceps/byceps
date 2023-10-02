"""
byceps.events.orga
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.brand.models import BrandID
from byceps.services.user.models.user import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _OrgaEvent(_BaseEvent):
    user_id: UserID
    user_screen_name: str | None
    brand_id: BrandID
    brand_title: str


@dataclass(frozen=True)
class OrgaStatusGrantedEvent(_OrgaEvent):
    pass


@dataclass(frozen=True)
class OrgaStatusRevokedEvent(_OrgaEvent):
    pass
