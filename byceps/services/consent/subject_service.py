"""
byceps.services.consent.subject_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Optional, Set

from ...database import db
from ...typing import BrandID

from .models.brand_requirement import BrandRequirement as DbBrandRequirement
from .models.consent import Consent as DbConsent
from .models.subject import Subject as DbSubject
from .transfer.models import Subject, SubjectID


# -------------------------------------------------------------------- #
# subjects


class UnknownSubjectId(ValueError):
    pass


def create_subject(
    name: str,
    title: str,
    type_: str,
    checkbox_label: str,
    checkbox_link_target: Optional[str],
) -> SubjectID:
    """Create a new subject."""
    subject = DbSubject(
        name, title, type_, checkbox_label, checkbox_link_target
    )

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
        subject.checkbox_label,
        subject.checkbox_link_target,
    )


# -------------------------------------------------------------------- #
# brand requirements


def create_brand_requirement(brand_id: BrandID, subject_id: SubjectID) -> None:
    """Create a brand requirement."""
    brand_requirement = DbBrandRequirement(brand_id, subject_id)

    db.session.add(brand_requirement)
    db.session.commit()


def delete_brand_requirement(brand_id: BrandID, subject_id: SubjectID) -> None:
    """Delete a brand requirement."""
    db.session.query(DbBrandRequirement) \
        .filter_by(brand_id=brand_id) \
        .filter_by(subject_id=subject_id) \
        .delete()

    db.session.commit()


def get_subjects_required_for_brand(brand_id: BrandID) -> Set[Subject]:
    """Return the subjects required for the brand."""
    rows = DbSubject.query \
        .join(DbBrandRequirement) \
        .filter(DbBrandRequirement.brand_id == brand_id) \
        .all()

    return {_db_entity_to_subject(row) for row in rows}
