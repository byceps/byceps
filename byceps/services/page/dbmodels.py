"""
byceps.services.page.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pages of database-stored content. Can contain HTML and template engine
syntax.

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.language.dbmodels import DbLanguage
from byceps.services.site.models import SiteID
from byceps.services.site_navigation.models import NavMenuID
from byceps.services.site_navigation.dbmodels import DbNavMenu
from byceps.services.user.dbmodels import DbUser
from byceps.services.user.models import UserID

from .models import PageID, PageVersionID


class DbPage(db.Model):
    """A content page.

    Any page is expected to have at least one version (the initial one).
    """

    __tablename__ = 'pages'
    __table_args__ = (
        db.UniqueConstraint('site_id', 'name', 'language_code'),
        db.UniqueConstraint('site_id', 'language_code', 'url_path'),
    )

    id: Mapped[PageID] = mapped_column(db.Uuid, primary_key=True)
    site_id: Mapped[SiteID] = mapped_column(
        db.UnicodeText, db.ForeignKey('sites.id'), index=True
    )
    name: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    language_code: Mapped[str] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('languages.code'),
        index=True,
    )
    language: Mapped[DbLanguage] = relationship()
    url_path: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    published: Mapped[bool]
    nav_menu_id: Mapped[NavMenuID | None] = mapped_column(
        db.Uuid, db.ForeignKey('site_nav_menus.id')
    )
    nav_menu: Mapped[DbNavMenu] = relationship()

    current_version = association_proxy(
        'current_version_association', 'version'
    )

    def __init__(
        self,
        page_id: PageID,
        site_id: SiteID,
        name: str,
        language_code: str,
        url_path: str,
    ) -> None:
        self.id = page_id
        self.site_id = site_id
        self.name = name
        self.language_code = language_code
        self.url_path = url_path
        self.published = False


class DbPageVersion(db.Model):
    """A snapshot of a page at a certain time."""

    __tablename__ = 'page_versions'

    id: Mapped[PageVersionID] = mapped_column(db.Uuid, primary_key=True)
    page_id: Mapped[PageID] = mapped_column(
        db.Uuid, db.ForeignKey('pages.id'), index=True
    )
    page: Mapped[DbPage] = relationship()
    created_at: Mapped[datetime]
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    creator: Mapped[DbUser] = relationship()
    title: Mapped[str] = mapped_column(db.UnicodeText)
    head: Mapped[str | None] = mapped_column(db.UnicodeText)
    body: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(
        self,
        version_id: PageVersionID,
        page: DbPage,
        created_at: datetime,
        creator_id: UserID,
        title: str,
        head: str | None,
        body: str,
    ) -> None:
        self.id = version_id
        self.page = page
        self.created_at = created_at
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


class DbCurrentPageVersionAssociation(db.Model):
    __tablename__ = 'page_current_versions'

    page_id: Mapped[PageID] = mapped_column(
        db.Uuid, db.ForeignKey('pages.id'), primary_key=True
    )
    page: Mapped[DbPage] = relationship(
        backref=db.backref('current_version_association', uselist=False)
    )
    version_id: Mapped[PageVersionID] = mapped_column(
        db.Uuid, db.ForeignKey('page_versions.id'), unique=True
    )
    version: Mapped[DbPageVersion] = relationship()

    def __init__(self, page: DbPage, version: DbPageVersion) -> None:
        self.page = page
        self.version = version
