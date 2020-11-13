"""
byceps.services.snippet.models.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Snippets of database-stored content. Can contain HTML and template
engine syntax. Can be embedded in other templates or mounted as full
page.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from ....database import BaseQuery, db, generate_uuid
from ....typing import UserID
from ....util.instances import ReprBuilder

from ...user.models.user import User

from ..transfer.models import Scope, SnippetType


class Snippet(db.Model):
    """A snippet.

    Each snippet is expected to have at least one version (the initial
    one).
    """

    __tablename__ = 'snippets'
    __table_args__ = (
        db.Index('ix_snippets_scope', 'scope_type', 'scope_name'),
        db.UniqueConstraint('scope_type', 'scope_name', 'name'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    scope_type = db.Column(db.UnicodeText, nullable=False)
    scope_name = db.Column(db.UnicodeText, nullable=False)
    name = db.Column(db.UnicodeText, index=True, nullable=False)
    _type = db.Column('type', db.UnicodeText, nullable=False)
    current_version = association_proxy('current_version_association', 'version')

    def __init__(self, scope: Scope, name: str, type_: SnippetType) -> None:
        self.scope_type = scope.type_
        self.scope_name = scope.name
        self.name = name
        self.type_ = type_

    @property
    def scope(self) -> Scope:
        return Scope(self.scope_type, self.scope_name)

    @hybrid_property
    def type_(self) -> SnippetType:
        return SnippetType[self._type]

    @type_.setter
    def type_(self, type_: SnippetType) -> None:
        assert type_ is not None
        self._type = type_.name

    @property
    def is_document(self) -> bool:
        return self.type_ == SnippetType.document

    @property
    def is_fragment(self) -> bool:
        return self.type_ == SnippetType.fragment

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('scope_type') \
            .add_with_lookup('scope_name') \
            .add_with_lookup('name') \
            .add('type', self._type) \
            .build()


class SnippetVersionQuery(BaseQuery):

    def latest_first(self) -> BaseQuery:
        return self.order_by(SnippetVersion.created_at.desc())


class SnippetVersion(db.Model):
    """A snapshot of a snippet at a certain time."""

    __tablename__ = 'snippet_versions'
    query_class = SnippetVersionQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), index=True, nullable=False)
    snippet = db.relationship(Snippet)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(User)
    title = db.Column(db.UnicodeText, nullable=True)
    head = db.Column(db.UnicodeText, nullable=True)
    body = db.Column(db.UnicodeText, nullable=False)
    image_url_path = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        snippet: Snippet,
        creator_id: UserID,
        title: Optional[str],
        head: Optional[str],
        body: str,
        image_url_path: Optional[str],
    ) -> None:
        self.snippet = snippet
        self.creator_id = creator_id
        self.title = title
        self.head = head
        self.body = body
        self.image_url_path = image_url_path

    @property
    def is_current(self) -> bool:
        """Return `True` if this version is the current version of the
        snippet it belongs to.
        """
        return self.id == self.snippet.current_version.id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('snippet') \
            .add_with_lookup('created_at') \
            .build()


class CurrentVersionAssociation(db.Model):
    __tablename__ = 'snippet_current_versions'

    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), primary_key=True)
    snippet = db.relationship(Snippet, backref=db.backref('current_version_association', uselist=False))
    version_id = db.Column(db.Uuid, db.ForeignKey('snippet_versions.id'), unique=True, nullable=False)
    version = db.relationship(SnippetVersion)

    def __init__(self, snippet: Snippet, version: SnippetVersion) -> None:
        self.snippet = snippet
        self.version = version
