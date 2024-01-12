"""
byceps.services.connected_external_accounts.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.user.models.user import UserID
from byceps.util.uuid import generate_uuid7


class DbConnectedExternalAccount(db.Model):
    """A connection from a BYCEPS user account to an external account."""

    __tablename__ = 'connected_external_accounts'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'service'),
        db.UniqueConstraint('service', 'external_id'),
        db.UniqueConstraint('service', 'external_name'),
    )

    id: Mapped[UUID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(db.DateTime)
    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    service: Mapped[str] = mapped_column(db.UnicodeText)
    external_id: Mapped[str | None] = mapped_column(db.UnicodeText)
    external_name: Mapped[str | None] = mapped_column(db.UnicodeText)

    def __init__(
        self,
        created_at: datetime,
        user_id: UserID,
        service: str,
        *,
        external_id: str | None = None,
        external_name: str | None = None,
    ) -> None:
        if not external_id and not external_name:
            raise ValueError(
                'Either external ID or external name must be given'
            )

        self.created_at = created_at
        self.user_id = user_id
        self.service = service
        self.external_id = external_id
        self.external_name = external_name
