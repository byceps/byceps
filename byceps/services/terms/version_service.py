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

from . import document_service
from .models.document import Document as DbDocument
from .models.version import Version as DbVersion
from .transfer.models import DocumentID, VersionID


def create_version(document_id: DocumentID, title: str,
                   snippet_version_id: SnippetVersionID,
                   consent_subject_id: ConsentSubjectID
                  ) -> DbVersion:
    """Create a new version of that document."""
    version = DbVersion(document_id, title, snippet_version_id,
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


def find_current_version_for_brand(brand_id: BrandID) -> Optional[DbVersion]:
    """Return the current version of the document configured for the
    brand, or `None` if none is configured for the brand or if the
    document has no current version set.
    """
    document_id = document_service.find_document_id_for_brand(brand_id)
    if not document_id:
        # Not configured for brand.
        return None

    document = document_service.find_document(document_id)
    if not document:
        raise ValueError(
            f'Unknown document ID "{document_id}" configured '
            f'for brand ID "{brand_id}".')

    if document.current_version_id is None:
        raise ValueError(
            f'No current version specified for document ID "{document_id}".')

    return find_version(document.current_version_id)


def get_versions(document_id: DocumentID) -> Sequence[DbVersion]:
    """Return all versions of the document, ordered by creation date,
    latest first.
    """
    return DbVersion.query \
        .join(DbDocument, DbVersion.document_id == DbDocument.id) \
        .filter(DbDocument.id == document_id) \
        .options(
            db.joinedload('snippet_version')
        ) \
        .order_by(DbVersion.created_at.desc()) \
        .all()
