"""
byceps.services.consent.consent_subject_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...database import db
from ...typing import BrandID

from .dbmodels.brand_requirement import DbBrandRequirement
from .dbmodels.consent import DbConsent
from .dbmodels.subject import DbSubject
from .models import Subject, SubjectID


class UnknownSubjectId(ValueError):
    pass


def create_subject(
    name: str,
    title: str,
    checkbox_label: str,
    checkbox_link_target: Optional[str],
) -> Subject:
    """Create a new subject."""
    db_subject = DbSubject(name, title, checkbox_label, checkbox_link_target)

    db.session.add(db_subject)
    db.session.commit()

    return _db_entity_to_subject(db_subject)


def get_subjects(subject_ids: set[SubjectID]) -> set[Subject]:
    """Return the subjects."""
    db_subjects = (
        db.session.query(DbSubject).filter(DbSubject.id.in_(subject_ids)).all()
    )

    subjects = {_db_entity_to_subject(db_subject) for db_subject in db_subjects}

    _check_for_unknown_subject_ids(subject_ids, subjects)

    return subjects


def _check_for_unknown_subject_ids(
    subject_ids: set[SubjectID], subjects: set[Subject]
) -> None:
    """Raise exception on unknown IDs."""
    found_subject_ids = {subject.id for subject in subjects}
    unknown_subject_ids = subject_ids.difference(found_subject_ids)
    if unknown_subject_ids:
        unknown_subject_ids_str = ', '.join(map(str, unknown_subject_ids))
        raise UnknownSubjectId(
            f'Unknown subject IDs: {unknown_subject_ids_str}'
        )


def get_subjects_with_consent_counts(
    *, limit_to_subject_ids: Optional[set[SubjectID]] = None
) -> dict[Subject, int]:
    """Return subjects and their consent counts."""
    query = db.session.query(
        DbSubject, db.func.count(DbConsent.user_id)
    ).outerjoin(DbConsent)

    if limit_to_subject_ids is not None:
        query = query.filter(DbSubject.id.in_(limit_to_subject_ids))

    db_subjects_and_consent_counts = query.group_by(DbSubject.id).all()

    return {
        _db_entity_to_subject(db_subject): consent_count
        for db_subject, consent_count in db_subjects_and_consent_counts
    }


def get_subject_ids_required_for_brand(brand_id: BrandID) -> set[SubjectID]:
    """Return the IDs of the subjects required for the brand."""
    subject_id_rows = (
        db.session.query(DbSubject.id)
        .join(DbBrandRequirement)
        .filter(DbBrandRequirement.brand_id == brand_id)
        .all()
    )

    return {subject_id_row[0] for subject_id_row in subject_id_rows}


def get_subjects_required_for_brand(brand_id: BrandID) -> set[Subject]:
    """Return the subjects required for the brand."""
    db_subjects = (
        db.session.query(DbSubject)
        .join(DbBrandRequirement)
        .filter(DbBrandRequirement.brand_id == brand_id)
        .all()
    )

    return {_db_entity_to_subject(db_subject) for db_subject in db_subjects}


def _db_entity_to_subject(db_subject: DbSubject) -> Subject:
    return Subject(
        id=db_subject.id,
        name=db_subject.name,
        title=db_subject.title,
        checkbox_label=db_subject.checkbox_label,
        checkbox_link_target=db_subject.checkbox_link_target,
    )
