"""
byceps.services.user.dbmodels.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.associationproxy import association_proxy

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...user_avatar.dbmodels import DbAvatarSelection


class DbUser(db.Model):
    """A user."""

    __tablename__ = 'users'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    screen_name = db.Column(db.UnicodeText, unique=True, nullable=True)
    email_address = db.Column(db.UnicodeText, unique=True, nullable=True)
    email_address_verified = db.Column(
        db.Boolean, default=False, nullable=False
    )
    initialized = db.Column(db.Boolean, default=False, nullable=False)
    suspended = db.Column(db.Boolean, default=False, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    locale = db.Column(db.UnicodeText, nullable=True)
    legacy_id = db.Column(db.UnicodeText, nullable=True)

    avatar = association_proxy(
        'avatar_selection',
        'avatar',
        creator=lambda avatar: DbAvatarSelection(None, avatar.id),
    )

    def __init__(
        self,
        created_at: datetime,
        screen_name: Optional[str],
        email_address: Optional[str],
        *,
        locale: Optional[str] = None,
        legacy_id: Optional[str] = None,
    ) -> None:
        self.created_at = created_at
        self.screen_name = screen_name
        self.email_address = email_address
        self.locale = locale
        self.legacy_id = legacy_id

    @property
    def avatar_url(self) -> Optional[str]:
        avatar = self.avatar
        return avatar.url if (avatar is not None) else None

    def __eq__(self, other) -> bool:
        return (other is not None) and (self.id == other.id)

    def __hash__(self) -> int:
        if self.id is None:
            raise ValueError(
                'User instance is unhashable because its id is None.'
            )

        return hash(self.id)

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('screen_name') \
            .build()
