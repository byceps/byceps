"""
byceps.services.terms.document_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db

from .models.document import Document as DbDocument
from .models.version import Version as DbVersion
from .transfer.models import Document, DocumentID, VersionID


def create_document(document_id: DocumentID, title: str) -> Document:
    """Create a terms of service document."""
    document = DbDocument(document_id, title)

    db.session.add(document)
    db.session.commit()

    return _db_entity_to_document(document)


def find_document(document_id: DocumentID) -> Optional[Document]:
    """Return the document with that ID, or `None` if not found."""
    document = DbDocument.query.get(document_id)

    if document is None:
        return None

    return _db_entity_to_document(document)


def set_current_version(document_id: DocumentID, version_id: VersionID
                       ) -> None:
    """Specify the current version of the document."""
    document = DbDocument.query.get(document_id)
    if document is None:
        raise ValueError(f'Unknown terms of service document ID "{document_id}"')

    version = DbVersion.query.get(version_id)
    if version is None:
        raise ValueError(f'Unknown terms of service version ID "{version_id}"')

    document.current_version_id = version.id
    db.session.commit()


def _db_entity_to_document(document: DbDocument) -> Document:
    return Document(
        document.id,
        document.title,
        document.current_version_id,
    )
