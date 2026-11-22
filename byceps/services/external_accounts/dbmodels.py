"""
byceps.services.external_accounts.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey, UniqueConstraint
from sqlalchemy.types import DateTime, UnicodeText, Uuid

from byceps.database import db
from byceps.services.user.models import UserID


class DbConnectedExternalAccount(db.Model):
    """A connection from a BYCEPS user account to an external account."""

    __tablename__ = 'connected_external_accounts'
    __table_args__ = (
        UniqueConstraint('user_id', 'service'),
        UniqueConstraint('service', 'external_id'),
        UniqueConstraint('service', 'external_name'),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[UserID] = mapped_column(
        Uuid, ForeignKey('users.id'), index=True
    )
    service: Mapped[str] = mapped_column(UnicodeText)
    external_id: Mapped[str | None] = mapped_column(UnicodeText)
    external_name: Mapped[str | None] = mapped_column(UnicodeText)

    def __init__(
        self,
        connection_id: UUID,
        created_at: datetime,
        user_id: UserID,
        service: str,
        external_id: str | None,
        external_name: str | None,
    ) -> None:
        if not external_id and not external_name:
            raise ValueError(
                'Either external ID or external name must be given'
            )

        self.id = connection_id
        self.created_at = created_at
        self.user_id = user_id
        self.service = service
        self.external_id = external_id
        self.external_name = external_name
