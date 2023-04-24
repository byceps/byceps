"""
byceps.services.connected_external_accounts.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.database import db, generate_uuid7
from byceps.typing import UserID


class DbConnectedExternalAccount(db.Model):
    """A connection from a BYCEPS user account to an external account."""

    __tablename__ = 'connected_external_accounts'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'service'),
        db.UniqueConstraint('service', 'external_id'),
        db.UniqueConstraint('service', 'external_name'),
    )

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False
    )
    service = db.Column(db.UnicodeText, nullable=False)
    external_id = db.Column(db.UnicodeText, nullable=True)
    external_name = db.Column(db.UnicodeText, nullable=True)

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
