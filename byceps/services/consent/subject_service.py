"""
byceps.services.consent.subject_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Optional

from ...database import db

from .models.consent import Consent as DbConsent
from .models.subject import Subject as DbSubject
from .transfer.models import Subject, SubjectID


def create_subject(name: str, title: str, type_: str) -> SubjectID:
    """Create a new subject."""
    subject = DbSubject(name, title, type_)

    db.session.add(subject)
    db.session.commit()

    return _db_entity_to_subject(subject)


def find_subject(subject_id: SubjectID) -> Optional[Subject]:
    """Return the subject with that id, or `None` if not found."""
    subject = DbSubject.query.get(subject_id)

    if subject is None:
        return None

    return _db_entity_to_subject(subject)


def get_subjects_with_consent_counts() -> Dict[Subject, int]:
    """Return all subjects."""
    rows = db.session \
        .query(
            DbSubject,
            db.func.count(DbConsent.user_id)
        ) \
        .outerjoin(DbConsent) \
        .group_by(DbSubject.id) \
        .all()

    return {_db_entity_to_subject(subject): consent_count
            for subject, consent_count in rows}


def _db_entity_to_subject(subject: DbSubject) -> Subject:
    return Subject(
        subject.id,
        subject.name,
        subject.title,
        subject.type_,
    )
