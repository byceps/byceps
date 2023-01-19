"""
byceps.services.consent.dbmodels.consent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from ....database import db
from ....typing import UserID

from ...user.dbmodels.user import DbUser

from ..models import SubjectID

from .subject import DbSubject


class DbConsent(db.Model):
    """A user's consent to a subject."""

    __tablename__ = 'consents'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(DbUser)
    subject_id = db.Column(
        db.Uuid, db.ForeignKey('consent_subjects.id'), primary_key=True
    )
    subject = db.relationship(DbSubject)
    expressed_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self, user_id: UserID, subject_id: SubjectID, expressed_at: datetime
    ) -> None:
        self.user_id = user_id
        self.subject_id = subject_id
        self.expressed_at = expressed_at
