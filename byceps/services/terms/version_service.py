"""
byceps.services.terms.version_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional, Sequence

from ...database import db

from .dbmodels.document import Document as DbDocument
from .dbmodels.version import Version as DbVersion
from .transfer.models import DocumentID, VersionID


def find_version(version_id: VersionID) -> Optional[DbVersion]:
    """Return the version with that ID, or `None` if not found."""
    return DbVersion.query.get(version_id)


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
