"""
byceps.services.terms.models.version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ....database import db, generate_uuid
from ....typing import BrandID
from ....util.instances import ReprBuilder

from ...brand.models.brand import Brand
from ...consent.models.subject import Subject as ConsentSubject
from ...consent.transfer.models import SubjectID as ConsentSubjectID
from ...snippet.models.snippet import SnippetVersion
from ...snippet.transfer.models import SnippetVersionID

from ..transfer.models import DocumentID

from . import document  # Make reference table available.


class Version(db.Model):
    """A specific version of a specific brand's terms and conditions."""
    __tablename__ = 'terms_versions'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship(Brand)
    document_id = db.Column(db.UnicodeText, db.ForeignKey('terms_documents.id'), index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    title = db.Column(db.UnicodeText, nullable=False)
    snippet_version_id = db.Column(db.Uuid, db.ForeignKey('snippet_versions.id'), index=True, nullable=False)
    snippet_version = db.relationship(SnippetVersion)
    consent_subject_id = db.Column(db.Uuid, db.ForeignKey('consent_subjects.id'), nullable=False)
    consent_subject = db.relationship(ConsentSubject)

    def __init__(self, brand_id: BrandID, document_id: DocumentID, title: str,
                 snippet_version_id: SnippetVersionID,
                 consent_subject_id: ConsentSubjectID
                ) -> None:
        self.brand_id = brand_id
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
            .add('brand', self.brand_id) \
            .add_with_lookup('document_id') \
            .add_with_lookup('created_at') \
            .add_with_lookup('title') \
            .build()
