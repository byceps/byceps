"""
byceps.services.page.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pages of database-stored content. Can contain HTML and template engine
syntax.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.associationproxy import association_proxy

from ...database import db, generate_uuid
from ...typing import UserID

from ..language.dbmodels import DbLanguage
from ..site.transfer.models import SiteID
from ..site_navigation.dbmodels import DbMenu
from ..user.dbmodels.user import DbUser


class DbPage(db.Model):
    """A content page.

    Any page is expected to have at least one version (the initial one).
    """

    __tablename__ = 'pages'
    __table_args__ = (
        db.UniqueConstraint('site_id', 'name'),
        db.UniqueConstraint('site_id', 'language_code', 'url_path'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    site_id = db.Column(
        db.UnicodeText, db.ForeignKey('sites.id'), index=True, nullable=False
    )
    name = db.Column(db.UnicodeText, index=True, nullable=False)
    language_code = db.Column(
        db.UnicodeText,
        db.ForeignKey('languages.code'),
        index=True,
        nullable=False,
    )
    language = db.relationship(DbLanguage)
    url_path = db.Column(db.UnicodeText, index=True, nullable=False)
    published = db.Column(db.Boolean, nullable=False)
    nav_menu_id = db.Column(
        db.Uuid, db.ForeignKey('site_nav_menus.id'), nullable=True
    )
    nav_menu = db.relationship(DbMenu)

    current_version = association_proxy(
        'current_version_association', 'version'
    )

    def __init__(
        self, site_id: SiteID, name: str, language_code: str, url_path: str
    ) -> None:
        self.site_id = site_id
        self.name = name
        self.language_code = language_code
        self.url_path = url_path
        self.published = False


class DbVersion(db.Model):
    """A snapshot of a page at a certain time."""

    __tablename__ = 'page_versions'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    page_id = db.Column(
        db.Uuid, db.ForeignKey('pages.id'), index=True, nullable=False
    )
    page = db.relationship(DbPage)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship(DbUser)
    title = db.Column(db.UnicodeText, nullable=False)
    head = db.Column(db.UnicodeText, nullable=True)
    body = db.Column(db.UnicodeText, nullable=False)

    def __init__(
        self,
        page: DbPage,
        creator_id: UserID,
        title: str,
        head: Optional[str],
        body: str,
    ) -> None:
        self.page = page
        self.creator_id = creator_id
        self.title = title
        self.head = head
        self.body = body

    @property
    def is_current(self) -> bool:
        """Return `True` if this version is the current version of the
        page it belongs to.
        """
        return self.id == self.page.current_version.id


class DbCurrentVersionAssociation(db.Model):
    __tablename__ = 'page_current_versions'

    page_id = db.Column(db.Uuid, db.ForeignKey('pages.id'), primary_key=True)
    page = db.relationship(
        DbPage, backref=db.backref('current_version_association', uselist=False)
    )
    version_id = db.Column(
        db.Uuid, db.ForeignKey('page_versions.id'), unique=True, nullable=False
    )
    version = db.relationship(DbVersion)

    def __init__(self, page: DbPage, version: DbVersion) -> None:
        self.page = page
        self.version = version
