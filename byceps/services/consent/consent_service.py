"""
byceps.services.consent.consent_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Iterable

from ...database import db
from ...typing import UserID

from .dbmodels.consent import DbConsent
from .dbmodels.subject import DbSubject
from .transfer.models import Consent, SubjectID


def consent_to_subject(
    user_id: UserID, subject_id: SubjectID, expressed_at: datetime
) -> None:
    """Store the user's consent to that subject."""
    consent_to_subjects(user_id, [subject_id], expressed_at)


def consent_to_subjects(
    user_id: UserID,
    subject_ids: Iterable[SubjectID],
    expressed_at: datetime,
) -> None:
    """Store the user's consent to these subjects."""
    for subject_id in subject_ids:
        consent = DbConsent(user_id, subject_id, expressed_at)
        db.session.add(consent)

    db.session.commit()


def count_consents_by_subject() -> dict[str, int]:
    """Return the number of given consents per subject."""
    rows = db.session \
        .query(
            DbSubject.name,
            db.func.count(DbConsent.user_id)
        ) \
        .outerjoin(DbConsent) \
        .group_by(DbSubject.name) \
        .all()

    return dict(rows)


def get_consents_by_user(user_id: UserID) -> set[Consent]:
    """Return the consents the user submitted."""
    consents = db.session \
        .query(DbConsent) \
        .filter_by(user_id=user_id) \
        .all()

    return {
        Consent(
            user_id=consent.user_id,
            subject_id=consent.subject_id,
            expressed_at=consent.expressed_at,
        )
        for consent in consents
    }


def get_unconsented_subject_ids(
    user_id: UserID, required_subject_ids: set[SubjectID]
) -> set[SubjectID]:
    """Return the IDs of the subjects the user has not consented to."""
    return {
        subject_id
        for subject_id in required_subject_ids
        if not has_user_consented_to_subject(user_id, subject_id)
    }


def has_user_consented_to_all_subjects(
    user_id: UserID, subject_ids: set[SubjectID]
) -> bool:
    """Return `True` if the user has consented to all given subjects."""
    return all(
        has_user_consented_to_subject(user_id, subject_id)
        for subject_id in subject_ids
    )


def has_user_consented_to_subject(
    user_id: UserID, subject_id: SubjectID
) -> bool:
    """Determine if the user has consented to the subject."""
    return db.session \
        .query(
            db.session
                .query(DbConsent)
                .filter_by(user_id=user_id)
                .filter_by(subject_id=subject_id)
                .exists()
        ) \
        .scalar()
