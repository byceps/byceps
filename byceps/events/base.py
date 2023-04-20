"""
byceps.events.base
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from byceps.typing import UserID


@dataclass(frozen=True)
class _BaseEvent:
    occurred_at: datetime
    initiator_id: UserID | None
    initiator_screen_name: str | None
