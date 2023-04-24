"""
byceps.services.connected_external_accounts.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from byceps.typing import UserID


@dataclass(frozen=True)
class ConnectedExternalAccount:
    id: UUID
    created_at: datetime
    user_id: UserID
    service: str
    external_id: str | None
    external_name: str | None
