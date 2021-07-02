"""
byceps.services.terms.document_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...database import db

from .dbmodels.document import Document as DbDocument
from .transfer.models import Document, DocumentID


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
        document.current_version_id,
    )
