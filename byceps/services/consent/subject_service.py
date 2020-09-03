"""
byceps.services.consent.subject_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Set

from ...database import db

from .models.consent import Consent as DbConsent
from .models.subject import Subject as DbSubject
from .transfer.models import Subject, SubjectID


class UnknownSubjectId(ValueError):
    pass


def create_subject(name: str, title: str, type_: str) -> SubjectID:
    """Create a new subject."""
    subject = DbSubject(name, title, type_)

    db.session.add(subject)
    db.session.commit()

    return _db_entity_to_subject(subject)


def get_subjects(subject_ids: Set[SubjectID]) -> Set[Subject]:
    """Return the subjects."""
    rows = DbSubject.query \
        .filter(DbSubject.id.in_(subject_ids)) \
        .all()

    subjects = {_db_entity_to_subject(row) for row in rows}

    _check_for_unknown_subject_ids(subject_ids, subjects)

    return subjects


def _check_for_unknown_subject_ids(
    subject_ids: Set[SubjectID], subjects: Set[Subject]
) -> None:
    """Raise exception on unknown IDs."""
    found_subject_ids = {subject.id for subject in subjects}
    unknown_subject_ids = subject_ids.difference(found_subject_ids)
    if unknown_subject_ids:
        unknown_subject_ids_str = ', '.join(map(str, unknown_subject_ids))
        raise UnknownSubjectId(
            f'Unknown subject IDs: {unknown_subject_ids_str}'
        )


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

    return {
        _db_entity_to_subject(subject): consent_count
        for subject, consent_count in rows
    }


def _db_entity_to_subject(subject: DbSubject) -> Subject:
    return Subject(
        subject.id,
        subject.name,
        subject.title,
        subject.type_,
    )
