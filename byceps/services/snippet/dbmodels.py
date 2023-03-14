"""
byceps.services.snippet.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Snippets of database-stored content. Can contain HTML and template
engine syntax. Can be embedded in other templates or mounted as full
page.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.ext.associationproxy import association_proxy

from ...database import db, generate_uuid7
from ...typing import UserID
from ...util.instances import ReprBuilder

from ..user.dbmodels.user import DbUser
from ..language.dbmodels import DbLanguage

from .models import Scope


class DbSnippet(db.Model):
    """A snippet.

    Each snippet is expected to have at least one version (the initial
    one).
    """

    __tablename__ = 'snippets'
    __table_args__ = (
        db.Index('ix_snippets_scope', 'scope_type', 'scope_name'),
        db.UniqueConstraint(
            'scope_type', 'scope_name', 'name', 'language_code'
        ),
    )

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    scope_type = db.Column(db.UnicodeText, nullable=False)
    scope_name = db.Column(db.UnicodeText, nullable=False)
    name = db.Column(db.UnicodeText, index=True, nullable=False)
    language_code = db.Column(
        db.UnicodeText,
        db.ForeignKey('languages.code'),
        index=True,
        nullable=False,
    )
    language = db.relationship(DbLanguage)
    current_version = association_proxy(
        'current_version_association', 'version'
    )

    def __init__(self, scope: Scope, name: str, language_code: str) -> None:
        self.scope_type = scope.type_
        self.scope_name = scope.name
        self.name = name
        self.language_code = language_code

    @property
    def scope(self) -> Scope:
        return Scope(self.scope_type, self.scope_name)

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('scope_type')
            .add_with_lookup('scope_name')
            .add_with_lookup('name')
            .build()
        )


class DbSnippetVersion(db.Model):
    """A snapshot of a snippet at a certain time."""

    __tablename__ = 'snippet_versions'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    snippet_id = db.Column(
        db.Uuid, db.ForeignKey('snippets.id'), index=True, nullable=False
    )
    snippet = db.relationship(DbSnippet)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(DbUser)
    body = db.Column(db.UnicodeText, nullable=False)

    def __init__(
        self, snippet: DbSnippet, creator_id: UserID, body: str
    ) -> None:
        self.snippet = snippet
        self.creator_id = creator_id
        self.body = body

    @property
    def is_current(self) -> bool:
        """Return `True` if this version is the current version of the
        snippet it belongs to.
        """
        return self.id == self.snippet.current_version.id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('snippet')
            .add_with_lookup('created_at')
            .build()
        )


class DbCurrentSnippetVersionAssociation(db.Model):
    __tablename__ = 'snippet_current_versions'

    snippet_id = db.Column(
        db.Uuid, db.ForeignKey('snippets.id'), primary_key=True
    )
    snippet = db.relationship(
        DbSnippet,
        backref=db.backref('current_version_association', uselist=False),
    )
    version_id = db.Column(
        db.Uuid,
        db.ForeignKey('snippet_versions.id'),
        unique=True,
        nullable=False,
    )
    version = db.relationship(DbSnippetVersion)

    def __init__(self, snippet: DbSnippet, version: DbSnippetVersion) -> None:
        self.snippet = snippet
        self.version = version
