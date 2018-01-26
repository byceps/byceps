"""
byceps.services.terms.models.consent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db
from ....typing import UserID

from ...user.models.user import User

from .version import Version, VersionID


ConsentContext = Enum('ConsentContext', ['account_creation', 'separate_action'])


class Consent(db.Model):
    """A user's consent to a specific version of a brand's terms and
    conditions.
    """
    __tablename__ = 'terms_consents'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User)
    version_id = db.Column(db.Uuid, db.ForeignKey('terms_versions.id'), primary_key=True)
    version = db.relationship(Version)
    expressed_at = db.Column(db.DateTime, default=datetime.now, primary_key=True)
    _context = db.Column('context', db.Unicode(20), primary_key=True)

    def __init__(self, user_id: UserID, version_id: VersionID,
                 context: ConsentContext) -> None:
        self.user_id = user_id
        self.version_id = version_id
        self.context = context

    @hybrid_property
    def context(self) -> ConsentContext:
        return ConsentContext[self._context]

    @context.setter
    def context(self, context: ConsentContext) -> None:
        assert context is not None
        self._context = context.name
