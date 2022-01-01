"""
byceps.events.base
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..typing import UserID


@dataclass(frozen=True)
class _BaseEvent:
    occurred_at: datetime
    initiator_id: Optional[UserID]
    initiator_screen_name: Optional[str]
