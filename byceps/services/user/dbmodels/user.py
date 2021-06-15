"""
byceps.services.user.dbmodels.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from flask import g
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.utils import cached_property

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...user_avatar.dbmodels import AvatarSelection

from ..transfer.models import User as UserDTO


class User(db.Model):
    """A user."""

    __tablename__ = 'users'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    screen_name = db.Column(db.UnicodeText, unique=True, nullable=True)
    email_address = db.Column(db.UnicodeText, unique=True, nullable=True)
    email_address_verified = db.Column(db.Boolean, default=False, nullable=False)
    initialized = db.Column(db.Boolean, default=False, nullable=False)
    suspended = db.Column(db.Boolean, default=False, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    legacy_id = db.Column(db.Integer)

    avatar = association_proxy('avatar_selection', 'avatar',
                               creator=lambda avatar:
                                    AvatarSelection(None, avatar.id))

    def __init__(
        self,
        created_at: datetime,
        screen_name: str,
        email_address: Optional[str],
    ) -> None:
        self.created_at = created_at
        self.screen_name = screen_name
        self.email_address = email_address

    @property
    def avatar_url(self) -> Optional[str]:
        avatar = self.avatar
        return avatar.url if (avatar is not None) else None

    @cached_property
    def is_orga(self) -> bool:
        party_id = getattr(g, 'party_id', None)

        if party_id is None:
            return False

        from ...orga_team import service as orga_team_service

        return orga_team_service.is_orga_for_party(self.id, party_id)

    def to_dto(self, *, include_avatar=False):
        avatar_url = self.avatar_url if include_avatar else None
        is_orga = False  # Information is deliberately not obtained here.

        return UserDTO(
            id=self.id,
            screen_name=self.screen_name,
            suspended=self.suspended,
            deleted=self.deleted,
            avatar_url=avatar_url,
            is_orga=is_orga,
        )

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
