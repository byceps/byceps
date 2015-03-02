# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.verification_token_models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy.ext.hybrid import hybrid_property

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..user.models import User


VerificationTokenPurpose = Enum(
    'VerificationTokenPurpose',
    ['email_address_confirmation', 'password_reset'])


class VerificationTokenQuery(BaseQuery):

    def for_purpose(self, purpose):
        return self.filter_by(_purpose=purpose.name)


class VerificationToken(db.Model):
    """A private token to authenticate as a certain user for a certain
    action.
    """
    __tablename__ = 'user_verification_tokens'
    query_class = VerificationTokenQuery

    token = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    user = db.relationship(User)
    _purpose = db.Column('purpose', db.Unicode(40), index=True, nullable=False)

    def __init__(self, user, purpose):
        self.user = user
        self.purpose = purpose

    @hybrid_property
    def purpose(self):
        return VerificationTokenPurpose[self._purpose]

    @purpose.setter
    def purpose(self, purpose):
        assert purpose is not None
        self._purpose = purpose.name

    @property
    def is_expired(self):
        """Return `True` if expired, i.e. it is no longer valid."""
        if self.purpose == VerificationTokenPurpose.password_reset:
            now = datetime.now()
            expires_after = timedelta(hours=24)
            return now >= (self.created_at + expires_after)
        else:
            return False

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('token') \
            .add('user', self.user.screen_name) \
            .add('purpose', self.purpose.name) \
            .build()
