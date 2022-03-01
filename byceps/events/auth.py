"""
byceps.events.auth
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from ..services.site.transfer.models import SiteID

from .base import _BaseEvent


@dataclass(frozen=True)
class UserLoggedIn(_BaseEvent):
    site_id: Optional[SiteID]
