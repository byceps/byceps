"""
byceps.services.orga.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent, EventBrand
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class _OrgaEvent(BaseEvent):
    user: User
    brand: EventBrand


@dataclass(frozen=True, kw_only=True)
class OrgaStatusGrantedEvent(_OrgaEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class OrgaStatusRevokedEvent(_OrgaEvent):
    pass
