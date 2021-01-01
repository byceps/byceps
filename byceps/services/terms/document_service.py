"""
byceps.services.terms.document_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...database import db
from ...typing import BrandID

from ..brand import settings_service as brand_settings_service

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


def set_current_version(document_id: DocumentID, version_id: VersionID) -> None:
    """Specify the current version of the document."""
    document = DbDocument.query.get(document_id)
    if document is None:
        raise ValueError(
            f'Unknown terms of service document ID "{document_id}"'
        )

    version = DbVersion.query.get(version_id)
    if version is None:
        raise ValueError(f'Unknown terms of service version ID "{version_id}"')

    document.current_version_id = version.id
    db.session.commit()


def find_document_id_for_brand(brand_id: BrandID) -> Optional[DocumentID]:
    """Return the document ID configured for the brand, or `None` if
    none is configured.
    """
    setting_name = 'terms_document_id'
    return brand_settings_service.find_setting_value(brand_id, setting_name)


def _db_entity_to_document(document: DbDocument) -> Document:
    return Document(
        document.id,
        document.title,
        document.current_version_id,
    )
