"""
byceps.services.terms.document_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db

from .models.document import Document as DbDocument
from .transfer.models import Document, DocumentID


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


def _db_entity_to_document(document: DbDocument) -> Document:
    return Document(
        document.id,
        document.title,
    )
