"""
byceps.events.base
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class _BaseEvent:
    occurred_at: datetime
