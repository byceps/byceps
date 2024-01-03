"""
byceps.services.consent.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.brand.models import BrandID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid4

from .models import ConsentSubjectID


class DbConsentSubject(db.Model):
    """A subject that requires users' consent."""

    __tablename__ = 'consent_subjects'

    id: Mapped[ConsentSubjectID] = mapped_column(
        db.Uuid, default=generate_uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    title: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    checkbox_label: Mapped[str] = mapped_column(db.UnicodeText)
    checkbox_link_target: Mapped[str | None] = mapped_column(db.UnicodeText)

    def __init__(
        self,
        name: str,
        title: str,
        checkbox_label: str,
        checkbox_link_target: str | None,
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

    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True
    )
    subject_id: Mapped[ConsentSubjectID] = mapped_column(
        db.Uuid, db.ForeignKey('consent_subjects.id'), primary_key=True
    )

    def __init__(self, brand_id: BrandID, subject_id: ConsentSubjectID) -> None:
        self.brand_id = brand_id
        self.subject_id = subject_id


class DbConsent(db.Model):
    """A user's consent to a subject."""

    __tablename__ = 'consents'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    user: Mapped[DbUser] = relationship(DbUser)
    subject_id: Mapped[ConsentSubjectID] = mapped_column(
        db.Uuid, db.ForeignKey('consent_subjects.id'), primary_key=True
    )
    subject: Mapped[DbConsentSubject] = relationship(DbConsentSubject)
    expressed_at: Mapped[datetime]

    def __init__(
        self,
        user_id: UserID,
        subject_id: ConsentSubjectID,
        expressed_at: datetime,
    ) -> None:
        self.user_id = user_id
        self.subject_id = subject_id
        self.expressed_at = expressed_at
