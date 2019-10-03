"""
byceps.services.terms.consent_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict

from ...database import db

from ..consent.models.consent import Consent
from ..consent.models.subject import Subject

from .models.version import Version
from .transfer.models import DocumentID, VersionID


def count_consents_for_document_versions(
    document_id: DocumentID
) -> Dict[VersionID, int]:
    """Return the number of consents for each version of the document."""
    rows = db.session \
        .query(
            Version.id,
            db.func.count(Consent.subject_id)
        ) \
        .outerjoin(Subject, Version.consent_subject) \
        .outerjoin(Consent) \
        .group_by(Version.id) \
        .filter(Version.document_id == document_id) \
        .all()

    return dict(rows)
