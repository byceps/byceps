"""
byceps.services.authn.identity_tag.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.user.models.user import UserID


class DbUserIdentityTag(db.Model):
    """A user-identifying tag.

    An identifier stored on an RFID transponder, in a barcode, etc.

    Multiple tags can refer to the same user, but each tag can only
    refer to a single user.

    Be aware that a user presenting a tag does not imply that the user
    actually is the one the tag refers to; the tag could be a clone or
    it could have been stolen. This is not that different from
    password-based authentication, but still needs to be kept in mind.
    """

    __tablename__ = 'authn_identity_tags'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    identifier: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    user_id: Mapped[UserID] = mapped_column(db.Uuid, db.ForeignKey('users.id'))
    note: Mapped[str | None] = mapped_column(db.UnicodeText)
    suspended: Mapped[bool]

    def __init__(
        self,
        tag_id: UUID,
        created_at: datetime,
        creator_id: UserID,
        identifier: str,
        user_id: UserID,
        note: str | None,
        suspended: bool,
    ) -> None:
        self.id = tag_id
        self.created_at = created_at
        self.creator_id = creator_id
        self.identifier = identifier
        self.user_id = user_id
        self.note = note
        self.suspended = suspended
