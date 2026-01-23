"""
byceps.services.external_accounts.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from byceps.services.user.models import UserID


@dataclass(frozen=True, kw_only=True)
class ConnectedExternalAccount:
    id: UUID
    created_at: datetime
    user_id: UserID
    service: str
    external_id: str | None
    external_name: str | None
