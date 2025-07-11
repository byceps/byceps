"""
byceps.services.orga.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent, EventBrand, EventUser


@dataclass(frozen=True, kw_only=True)
class _OrgaEvent(_BaseEvent):
    user: EventUser
    brand: EventBrand


@dataclass(frozen=True, kw_only=True)
class OrgaStatusGrantedEvent(_OrgaEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class OrgaStatusRevokedEvent(_OrgaEvent):
    pass
