"""
byceps.events.auth
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from byceps.services.site.models import SiteID

from .base import _BaseEvent


@dataclass(frozen=True)
class UserLoggedIn(_BaseEvent):
    site_id: Optional[SiteID]
