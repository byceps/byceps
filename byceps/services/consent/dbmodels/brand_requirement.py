"""
byceps.services.consent.dbmodels.brand_requirement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....database import db
from ....typing import BrandID

from ..transfer.models import SubjectID


class BrandRequirement(db.Model):
    """A consent requirement for a brand."""

    __tablename__ = 'consent_brand_requirements'

    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True)
    subject_id = db.Column(db.Uuid, db.ForeignKey('consent_subjects.id'), primary_key=True)

    def __init__(self, brand_id: BrandID, subject_id: SubjectID) -> None:
        self.brand_id = brand_id
        self.subject_id = subject_id
