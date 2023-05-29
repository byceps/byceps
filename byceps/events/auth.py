"""
byceps.events.auth
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.site.models import SiteID

from .base import _BaseEvent


@dataclass(frozen=True)
class UserLoggedInEvent(_BaseEvent):
    site_id: SiteID | None
    site_title: str | None
