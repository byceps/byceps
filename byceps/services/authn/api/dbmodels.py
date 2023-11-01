"""
byceps.services.authn.api.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.authz.models import PermissionID
from byceps.services.user.models.user import UserID


class DbApiToken(db.Model):
    """An authentication and authorization token for API clients."""

    __tablename__ = 'api_tokens'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    token: Mapped[str] = mapped_column(db.UnicodeText)
    permissions: Mapped[list[PermissionID]] = mapped_column(
        MutableList.as_mutable(db.JSONB)
    )
    description: Mapped[str | None] = mapped_column(db.UnicodeText)
    suspended: Mapped[bool]

    def __init__(
        self,
        api_token_id: UUID,
        created_at: datetime,
        creator_id: UserID,
        token: str,
        permissions: frozenset[PermissionID],
        description: str | None,
        suspended: bool,
    ) -> None:
        self.id = api_token_id
        self.created_at = created_at
        self.creator_id = creator_id
        self.token = token
        self.permissions = list(permissions)
        self.description = description
        self.suspended = suspended
