"""
byceps.services.snippet.models.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Snippets of database-stored content. Can contain HTML and template
engine syntax. Can be embedded in other templates or mounted as full
page.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from enum import Enum
from typing import NewType, Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from ....database import BaseQuery, db, generate_uuid
from ....typing import PartyID, UserID
from ....util.instances import ReprBuilder

from ...party.models.party import Party
from ...user.models.user import User


SnippetType = Enum('SnippetType', ['document', 'fragment'])


SnippetID = NewType('SnippetID', UUID)


class SnippetQuery(BaseQuery):

    def for_party_id(self, party_id: PartyID) -> BaseQuery:
        return self.filter_by(party_id=party_id)


class Snippet(db.Model):
    """A snippet.

    Each snippet is expected to have at least one version (the initial
    one).
    """
    __tablename__ = 'snippets'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'name'),
    )
    query_class = SnippetQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(40), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party)
    name = db.Column(db.Unicode(40), index=True, nullable=False)
    _type = db.Column('type', db.Unicode(8), nullable=False)
    current_version = association_proxy('current_version_association', 'version')

    def __init__(self, party_id: PartyID, name: str, type_: SnippetType) -> None:
        self.party_id = party_id
        self.name = name
        self.type_ = type_

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

    def get_versions(self) -> Sequence['SnippetVersion']:
        """Return all versions, sorted from most recent to oldest."""
        return SnippetVersion.query.for_snippet(self).latest_first().all()

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add_with_lookup('name') \
            .add('type', self._type) \
            .build()


SnippetVersionID = NewType('SnippetVersionID', UUID)


class SnippetVersionQuery(BaseQuery):

    def for_snippet(self, snippet: Snippet) -> BaseQuery:
        return self.filter_by(snippet=snippet)

    def latest_first(self) -> BaseQuery:
        return self.order_by(SnippetVersion.created_at.desc())


class SnippetVersion(db.Model):
    """A snapshot of a snippet at a certain time."""
    __tablename__ = 'snippet_versions'
    query_class = SnippetVersionQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    snippet_id = db.Column(db.Uuid, db.ForeignKey('snippets.id'), index=True, nullable=False)
    snippet = db.relationship(Snippet)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(User)
    title = db.Column(db.Unicode(80), nullable=True)
    head = db.Column(db.UnicodeText, nullable=True)
    body = db.Column(db.UnicodeText, nullable=False)
    image_url_path = db.Column(db.Unicode(80), nullable=True)

    def __init__(self, snippet: Snippet, creator_id: UserID,
                 title: Optional[str], head: Optional[str], body: str,
                 image_url_path: Optional[str]) -> None:
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
