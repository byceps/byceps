"""
byceps.services.authn.api.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from byceps.services.authz.models import PermissionID
from byceps.services.user.models import UserID


@dataclass(frozen=True, kw_only=True)
class ApiToken:
    id: UUID
    created_at: datetime
    creator_id: UserID
    token: str
    permissions: frozenset[PermissionID]
    description: str | None
    suspended: bool
