"""
byceps.services.terms.consent_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, Sequence

from ...database import db
from ...typing import BrandID, UserID

from ..verification_token.models import Token

from .models.consent import Consent, ConsentContext
from .models.version import Version, VersionID


def build_consent_on_account_creation(user_id: UserID, version_id: VersionID,
                                      expressed_at: datetime) -> Consent:
    """Create user's consent to that version expressed on account creation."""
    context = ConsentContext.account_creation
    return Consent(user_id, version_id, expressed_at, context)


def build_consent_on_separate_action(user_id: UserID, version_id: VersionID,
                                     expressed_at: datetime) -> Consent:
    """Create user's consent to that version expressed through a
    separate action.
    """
    context = ConsentContext.separate_action
    return Consent(user_id, version_id, expressed_at, context)


def consent_to_version_on_separate_action(version_id: VersionID,
                                          expressed_at: datetime,
                                          verification_token: Token) -> None:
    """Store the user's consent to that version, and invalidate the
    verification token.
    """
    user_id = verification_token.user_id
    db.session.delete(verification_token)

    consent = build_consent_on_separate_action(user_id, version_id, expressed_at)
    db.session.add(consent)

    db.session.commit()


def get_consents_by_user(user_id: UserID) -> Sequence[Consent]:
    """Return the consents the user submitted."""
    return Consent.query \
        .filter_by(user_id=user_id) \
        .all()


def count_user_consents_for_versions_of_brand(brand_id: BrandID
                                             ) -> Dict[VersionID, int]:
    """Return the number of user consents for each version of that brand."""
    rows = db.session \
        .query(
            Version.id,
            db.func.count(Consent.version_id)
        ) \
        .outerjoin(Consent) \
        .group_by(Version.id) \
        .filter(Version.brand_id == brand_id) \
        .all()

    return dict(rows)


def has_user_accepted_version(user_id: UserID, version_id: VersionID) -> bool:
    """Tell if the user has accepted the specified version of the terms."""
    return db.session \
        .query(
            db.session \
                .query(Consent) \
                .filter_by(user_id=user_id) \
                .filter_by(version_id=version_id) \
                .exists()
        ) \
        .scalar()
