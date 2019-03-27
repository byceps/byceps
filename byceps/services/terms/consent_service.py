"""
byceps.services.terms.consent_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict

from ...database import db
from ...typing import BrandID, UserID

from ..brand import settings_service as brand_settings_service
from ..consent.models.consent import Consent
from ..consent.models.subject import Subject

from .models.version import Version
from .transfer.models import VersionID


def is_consent_required_for_brand(brand_id: BrandID) -> bool:
    """Return `True` if consent to the brand's terms of service is
    required.

    By default, consent is required. It can be disabled by configuring
    the string `false` for the brand setting `terms_consent_required`.
    """
    value = brand_settings_service \
        .find_setting_value(brand_id, 'terms_consent_required')

    return value != 'false'


def count_user_consents_for_versions_of_brand(brand_id: BrandID
                                             ) -> Dict[VersionID, int]:
    """Return the number of user consents for each version of that brand."""
    rows = db.session \
        .query(
            Version.id,
            db.func.count(Consent.subject_id)
        ) \
        .outerjoin(Subject) \
        .outerjoin(Consent) \
        .group_by(Version.id) \
        .filter(Version.brand_id == brand_id) \
        .all()

    return dict(rows)


def has_user_accepted_version(user_id: UserID, version_id: VersionID) -> bool:
    """Tell if the user has accepted the specified version of the terms."""
    return db.session \
        .query(
            db.session
                .query(Consent)
                .join(Subject)
                .join(Version)
                .filter(Consent.user_id == user_id)
                .filter(Version.id == version_id)
                .exists()
        ) \
        .scalar()
