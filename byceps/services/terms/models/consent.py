"""
byceps.services.terms.models.consent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db
from ....typing import UserID

from ...user.models.user import User

from .version import Version, VersionID


class Consent(db.Model):
    """A user's consent to a specific version of a brand's terms and
    conditions.
    """
    __tablename__ = 'terms_consents'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User)
    version_id = db.Column(db.Uuid, db.ForeignKey('terms_versions.id'), primary_key=True)
    version = db.relationship(Version)
    expressed_at = db.Column(db.DateTime, primary_key=True)

    def __init__(self, user_id: UserID, version_id: VersionID,
                 expressed_at: datetime) -> None:
        self.user_id = user_id
        self.version_id = version_id
        self.expressed_at = expressed_at
