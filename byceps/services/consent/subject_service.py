"""
byceps.services.consent.subject_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db

from .models.subject import Subject as DbSubject
from .transfer.models import Subject, SubjectID


def create_subject(name: str, title: str) -> SubjectID:
    """Create a new subject."""
    subject = DbSubject(name, title)

    db.session.add(subject)
    db.session.commit()

    return _db_entity_to_subject(subject)


def find_subject(subject_id: SubjectID) -> Optional[Subject]:
    """Return the subject with that id, or `None` if not found."""
    subject = DbSubject.query.get(subject_id)

    if subject is None:
        return None

    return _db_entity_to_subject(subject)


def _db_entity_to_subject(subject: DbSubject) -> Subject:
    return Subject(
        subject.id,
        subject.name,
        subject.title,
    )
