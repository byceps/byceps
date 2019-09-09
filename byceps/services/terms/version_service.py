"""
byceps.services.terms.version_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import BrandID

from ..consent.transfer.models import SubjectID as ConsentSubjectID
from ..snippet.transfer.models import SnippetVersionID

from .models.document import Document as DbDocument
from .models.version import Version as DbVersion
from .transfer.models import DocumentID, VersionID


def create_version(brand_id: BrandID, document_id: DocumentID, title: str,
                   snippet_version_id: SnippetVersionID,
                   consent_subject_id: ConsentSubjectID
                  ) -> DbVersion:
    """Create a new version of the terms for that brand."""
    version = DbVersion(brand_id, document_id, title, snippet_version_id,
                        consent_subject_id)

    db.session.add(version)
    db.session.commit()

    return version


def find_version(version_id: VersionID) -> Optional[DbVersion]:
    """Return the version with that ID, or `None` if not found."""
    return DbVersion.query.get(version_id)


def find_version_for_consent_subject_id(consent_subject_id: ConsentSubjectID
                                       ) -> Optional[DbVersion]:
    """Return the version with that consent subject ID, or `None` if
    not found.
    """
    return DbVersion.query \
        .filter_by(consent_subject_id=consent_subject_id) \
        .one_or_none()


def find_current_version(document_id: DocumentID) -> Optional[DbVersion]:
    """Return the current version of the document, or `None` if none is
    configured.
    """
    return DbVersion.query \
        .join(DbDocument, DbDocument.current_version_id == DbVersion.id) \
        .filter(DbDocument.id == document_id) \
        .one_or_none()


def get_versions_for_brand(brand_id: BrandID) -> Sequence[DbVersion]:
    """Return all versions for that brand, ordered by creation date,
    latest first.
    """
    return DbVersion.query \
        .filter_by(brand_id=brand_id) \
        .options(
            db.joinedload('snippet_version')
        ) \
        .order_by(DbVersion.created_at.desc()) \
        .all()
