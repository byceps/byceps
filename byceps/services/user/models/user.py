# -*- coding: utf-8 -*-

"""
byceps.services.user.models.user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from datetime import datetime
from uuid import UUID

from flask import g
from sqlalchemy.ext.associationproxy import association_proxy

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...user_avatar.models import AvatarSelection


GUEST_USER_ID = UUID('00000000-0000-0000-0000-000000000000')


class AnonymousUser(object):

    id = GUEST_USER_ID
    enabled = False

    @property
    def is_anonymous(self):
        return True

    @property
    def is_active(self):
        return False

    def has_permission(self, permission):
        return False

    def has_any_permission(self, *permissions):
        return False

    @property
    def avatar(self):
        return None

    @property
    def avatar_url(self):
        return None

    @property
    def is_orga(self):
        return False

    def is_orga_for_party(self, party):
        return False

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class User(db.Model):
    """A user."""
    __tablename__ = 'users'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    screen_name = db.Column(db.Unicode(40), unique=True, nullable=False)
    email_address = db.Column(db.Unicode(80), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    legacy_id = db.Column(db.Integer)

    avatar = association_proxy('avatar_selection', 'avatar',
                               creator=lambda avatar:
                                    AvatarSelection(None, avatar.id))

    def __init__(self, screen_name, email_address):
        self.screen_name = screen_name
        self.email_address = email_address

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.enabled

    @property
    def avatar_url(self):
        avatar = self.avatar
        return avatar.url if (avatar is not None) else None

    def has_permission(self, permission):
        return permission in self.permissions

    def has_any_permission(self, *permissions):
        return any(map(self.has_permission, permissions))

    @property
    def is_orga(self):
        party = getattr(g, 'party', None)
        return (party is not None) and self.is_orga_for_party(party)

    def is_orga_for_party(self, party):
        parties = {ms.orga_team.party for ms in self.orga_team_memberships}
        return party in parties

    def __eq__(self, other):
        return (other is not None) and (self.id == other.id)

    def __hash__(self):
        if self.id is None:
            raise ValueError('User instance is unhashable because its id is None.')

        return hash(self.id)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('screen_name') \
            .build()


UserTuple = namedtuple('UserTuple', 'id, screen_name, avatar_url, is_orga')
