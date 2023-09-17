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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.language.dbmodels import DbLanguage
from byceps.services.user.dbmodels.user import DbUser
from byceps.typing import UserID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .models import SnippetID, SnippetScope, SnippetVersionID


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

    id: Mapped[SnippetID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    scope_type: Mapped[str] = mapped_column(db.UnicodeText)
    scope_name: Mapped[str] = mapped_column(db.UnicodeText)
    name: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    language_code: Mapped[str] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('languages.code'),
        index=True,
    )
    language: Mapped[DbLanguage] = relationship(DbLanguage)
    current_version = association_proxy(
        'current_version_association', 'version'
    )

    def __init__(
        self, scope: SnippetScope, name: str, language_code: str
    ) -> None:
        self.scope_type = scope.type_
        self.scope_name = scope.name
        self.name = name
        self.language_code = language_code

    @property
    def scope(self) -> SnippetScope:
        return SnippetScope(self.scope_type, self.scope_name)

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

    id: Mapped[SnippetVersionID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    snippet_id: Mapped[SnippetID] = mapped_column(
        db.Uuid, db.ForeignKey('snippets.id'), index=True
    )
    snippet: Mapped[DbSnippet] = relationship(DbSnippet)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, default=datetime.utcnow
    )
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    creator: Mapped[DbUser] = relationship(DbUser)
    body: Mapped[str] = mapped_column(db.UnicodeText)

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

    snippet_id: Mapped[SnippetID] = mapped_column(
        db.Uuid, db.ForeignKey('snippets.id'), primary_key=True
    )
    snippet: Mapped[DbSnippet] = relationship(
        DbSnippet,
        backref=db.backref('current_version_association', uselist=False),
    )
    version_id: Mapped[SnippetVersionID] = mapped_column(
        db.Uuid,
        db.ForeignKey('snippet_versions.id'),
        unique=True,
    )
    version: Mapped[DbSnippetVersion] = relationship(DbSnippetVersion)

    def __init__(self, snippet: DbSnippet, version: DbSnippetVersion) -> None:
        self.snippet = snippet
        self.version = version
