"""
byceps.services.consent.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from ...database import db, generate_uuid4
from ...typing import BrandID, UserID
from ...util.instances import ReprBuilder

from ..user.dbmodels.user import DbUser

from .models import ConsentSubjectID


class DbConsentSubject(db.Model):
    """A subject that requires users' consent."""

    __tablename__ = 'consent_subjects'

    id = db.Column(db.Uuid, default=generate_uuid4, primary_key=True)
    name = db.Column(db.UnicodeText, unique=True, nullable=False)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    checkbox_label = db.Column(db.UnicodeText, nullable=False)
    checkbox_link_target = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        name: str,
        title: str,
        checkbox_label: str,
        checkbox_link_target: Optional[str],
    ) -> None:
        self.name = name
        self.title = title
        self.checkbox_label = checkbox_label
        self.checkbox_link_target = checkbox_link_target

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('name')
            .add_with_lookup('title')
            .build()
        )


class DbConsentBrandRequirement(db.Model):
    """A consent requirement for a brand."""

    __tablename__ = 'consent_brand_requirements'

    brand_id = db.Column(
        db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True
    )
    subject_id = db.Column(
        db.Uuid, db.ForeignKey('consent_subjects.id'), primary_key=True
    )

    def __init__(self, brand_id: BrandID, subject_id: ConsentSubjectID) -> None:
        self.brand_id = brand_id
        self.subject_id = subject_id


class DbConsent(db.Model):
    """A user's consent to a subject."""

    __tablename__ = 'consents'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(DbUser)
    subject_id = db.Column(
        db.Uuid, db.ForeignKey('consent_subjects.id'), primary_key=True
    )
    subject = db.relationship(DbConsentSubject)
    expressed_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self,
        user_id: UserID,
        subject_id: ConsentSubjectID,
        expressed_at: datetime,
    ) -> None:
        self.user_id = user_id
        self.subject_id = subject_id
        self.expressed_at = expressed_at
