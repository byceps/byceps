"""
byceps.services.consent.consent_subject_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import select

from ...database import db
from ...typing import BrandID

from .dbmodels import DbConsent, DbConsentBrandRequirement, DbConsentSubject
from .models import ConsentSubject, ConsentSubjectID


class UnknownSubjectId(ValueError):
    pass


def create_subject(
    name: str,
    title: str,
    checkbox_label: str,
    checkbox_link_target: Optional[str],
) -> ConsentSubject:
    """Create a new subject."""
    db_subject = DbConsentSubject(
        name, title, checkbox_label, checkbox_link_target
    )

    db.session.add(db_subject)
    db.session.commit()

    return _db_entity_to_subject(db_subject)


def get_subjects(subject_ids: set[ConsentSubjectID]) -> set[ConsentSubject]:
    """Return the subjects."""
    db_subjects = db.session.scalars(
        select(DbConsentSubject).filter(DbConsentSubject.id.in_(subject_ids))
    ).all()

    subjects = {_db_entity_to_subject(db_subject) for db_subject in db_subjects}

    _check_for_unknown_subject_ids(subject_ids, subjects)

    return subjects


def _check_for_unknown_subject_ids(
    subject_ids: set[ConsentSubjectID], subjects: set[ConsentSubject]
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
    *, limit_to_subject_ids: Optional[set[ConsentSubjectID]] = None
) -> dict[ConsentSubject, int]:
    """Return subjects and their consent counts."""
    stmt = select(DbConsentSubject, db.func.count(DbConsent.user_id)).outerjoin(
        DbConsent
    )

    if limit_to_subject_ids is not None:
        stmt = stmt.filter(DbConsentSubject.id.in_(limit_to_subject_ids))

    stmt = stmt.group_by(DbConsentSubject.id)

    db_subjects_and_consent_counts = db.session.execute(stmt).all()

    return {
        _db_entity_to_subject(db_subject): consent_count
        for db_subject, consent_count in db_subjects_and_consent_counts
    }


def get_subject_ids_required_for_brand(
    brand_id: BrandID,
) -> set[ConsentSubjectID]:
    """Return the IDs of the subjects required for the brand."""
    subject_ids = db.session.scalars(
        select(DbConsentSubject.id)
        .join(DbConsentBrandRequirement)
        .filter(DbConsentBrandRequirement.brand_id == brand_id)
    ).all()

    return set(subject_ids)


def get_subjects_required_for_brand(brand_id: BrandID) -> set[ConsentSubject]:
    """Return the subjects required for the brand."""
    db_subjects = db.session.scalars(
        select(DbConsentSubject)
        .join(DbConsentBrandRequirement)
        .filter(DbConsentBrandRequirement.brand_id == brand_id)
    ).all()

    return {_db_entity_to_subject(db_subject) for db_subject in db_subjects}


def _db_entity_to_subject(db_subject: DbConsentSubject) -> ConsentSubject:
    return ConsentSubject(
        id=db_subject.id,
        name=db_subject.name,
        title=db_subject.title,
        checkbox_label=db_subject.checkbox_label,
        checkbox_link_target=db_subject.checkbox_link_target,
    )
