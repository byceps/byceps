"""
byceps.services.terms.consent_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, Sequence

from ...database import db
from ...typing import BrandID, UserID

from ..brand import settings_service as brand_settings_service
from ..verification_token.models import Token

from .models.consent import Consent
from .models.version import Version, VersionID


def is_consent_required_for_brand(brand_id: BrandID) -> bool:
    """Return `True` if consent to the brand's terms of service is
    required.

    By default, consent is required. It can be disabled by configuring
    the string `false` for the brand setting `terms_consent_required`.
    """
    value = brand_settings_service \
        .find_setting_value(brand_id, 'terms_consent_required')

    return value != 'false'


def build_consent(user_id: UserID, version_id: VersionID, expressed_at: datetime
                 ) -> Consent:
    """Create user's consent to that version."""
    return Consent(user_id, version_id, expressed_at)


def consent_to_version(version_id: VersionID, expressed_at: datetime,
                       verification_token: Token
                      ) -> None:
    """Store the user's consent to that version, and invalidate the
    verification token.
    """
    user_id = verification_token.user_id
    db.session.delete(verification_token)

    consent = build_consent(user_id, version_id, expressed_at)
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
