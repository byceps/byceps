"""
byceps.services.terms.consent_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict

from ...database import db
from ...typing import BrandID

from ..consent.models.consent import Consent
from ..consent.models.subject import Subject

from .models.version import Version
from .transfer.models import VersionID


def count_user_consents_for_versions_of_brand(brand_id: BrandID
                                             ) -> Dict[VersionID, int]:
    """Return the number of user consents for each version of that brand."""
    rows = db.session \
        .query(
            Version.id,
            db.func.count(Consent.subject_id)
        ) \
        .outerjoin(Subject, Version.consent_subject) \
        .outerjoin(Consent) \
        .group_by(Version.id) \
        .filter(Version.brand_id == brand_id) \
        .all()

    return dict(rows)
