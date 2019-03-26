"""
byceps.services.consent.subject_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db
from ...typing import BrandID

from .models.version import Subject
from .transfer.models import SubjectID


def create_subject(brand_id: BrandID, name: str) -> SubjectID:
    """Create a new subject."""
    subject = Subject(brand_id, name)

    db.session.add(subject)
    db.session.commit()

    return subject


def find_subject(subject_id: SubjectID) -> Optional[Subject]:
    """Return the subject with that id, or `None` if not found."""
    return Subject.query.get(subject_id)
