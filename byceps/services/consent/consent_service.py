"""
byceps.services.consent.consent_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, Sequence

from ...database import db
from ...typing import UserID

from ..verification_token.models import Token

from .models.consent import Consent as DbConsent
from .models.subject import Subject as DbSubject
from .transfer.models import SubjectID


def build_consent(
    user_id: UserID, subject_id: SubjectID, expressed_at: datetime
) -> DbConsent:
    """Create user's consent to that subject."""
    return DbConsent(user_id, subject_id, expressed_at)


def consent_to_subject(
    subject_id: SubjectID, expressed_at: datetime, verification_token: Token
) -> None:
    """Store the user's consent to that subject, and invalidate the
    verification token.
    """
    consent_to_subjects([subject_id], expressed_at, verification_token)


def consent_to_subjects(
    subject_ids: Sequence[SubjectID],
    expressed_at: datetime,
    verification_token: Token,
) -> None:
    """Store the user's consent to these subjects, and invalidate the
    verification token.
    """
    user_id = verification_token.user_id
    db.session.delete(verification_token)

    for subject_id in subject_ids:
        consent = build_consent(user_id, subject_id, expressed_at)
        db.session.add(consent)

    db.session.commit()


def count_consents_by_subject() -> Dict[str, int]:
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


def get_consents_by_user(user_id: UserID) -> Sequence[DbConsent]:
    """Return the consents the user submitted."""
    return DbConsent.query \
        .filter_by(user_id=user_id) \
        .all()


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
