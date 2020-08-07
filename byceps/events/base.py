"""
byceps.events.base
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..typing import UserID


@dataclass(frozen=True)
class _BaseEvent:
    occurred_at: datetime
    initiator_id: Optional[UserID]
