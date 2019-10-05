"""
byceps.services.terms.models.version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...consent.models.subject import Subject as ConsentSubject
from ...consent.transfer.models import SubjectID as ConsentSubjectID
from ...snippet.models.snippet import SnippetVersion
from ...snippet.transfer.models import SnippetVersionID

from ..transfer.models import DocumentID

from .document import Document


class Version(db.Model):
    """A specific version of a terms and conditions document."""

    __tablename__ = 'terms_versions'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    document_id = db.Column(db.UnicodeText, db.ForeignKey('terms_documents.id', name='terms_versions_document_id_fkey'), index=True, nullable=False)
    document = db.relationship(Document, foreign_keys=[document_id])
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    title = db.Column(db.UnicodeText, nullable=False)
    snippet_version_id = db.Column(db.Uuid, db.ForeignKey('snippet_versions.id'), index=True, nullable=False)
    snippet_version = db.relationship(SnippetVersion)
    consent_subject_id = db.Column(db.Uuid, db.ForeignKey('consent_subjects.id'), nullable=False)
    consent_subject = db.relationship(ConsentSubject)

    def __init__(
        self,
        document_id: DocumentID,
        title: str,
        snippet_version_id: SnippetVersionID,
        consent_subject_id: ConsentSubjectID,
    ) -> None:
        self.document_id = document_id
        self.title = title
        self.snippet_version_id = snippet_version_id
        self.consent_subject_id = consent_subject_id

    @property
    def body(self) -> str:
        return self.snippet_version.body

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('document_id') \
            .add_with_lookup('created_at') \
            .add_with_lookup('title') \
            .build()
