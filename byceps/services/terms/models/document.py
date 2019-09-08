"""
byceps.services.terms.models.document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....util.instances import ReprBuilder

from ..transfer.models import DocumentID


class Document(db.Model):
    """A terms of service document."""
    __tablename__ = 'terms_documents'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    current_version_id = db.Column(db.Uuid, db.ForeignKey('terms_versions.id'), nullable=True)

    def __init__(self, document_id: DocumentID, title: str) -> None:
        self.id = document_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
