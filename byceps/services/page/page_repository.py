"""
byceps.services.page.page_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.site.models import SiteID
from byceps.services.site_navigation.models import NavMenuID
from byceps.services.user.models import UserID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .dbmodels import DbCurrentPageVersionAssociation, DbPage, DbPageVersion
from .errors import PageDeletionFailedError
from .models import PageID, PageVersionID


def create_page(
    site_id: SiteID,
    name: str,
    language_code: str,
    url_path: str,
    created_at: datetime,
    creator_id: UserID,
    title: str,
    head: str | None,
    body: str,
) -> tuple[DbPage, DbPageVersion]:
    """Create a page and its initial version."""
    page_id = PageID(generate_uuid7())
    version_id = PageVersionID(generate_uuid7())

    db_page = DbPage(page_id, site_id, name, language_code, url_path)
    db.session.add(db_page)

    db_version = DbPageVersion(
        version_id, db_page, created_at, creator_id, title, head, body
    )
    db.session.add(db_version)

    db_current_version_association = DbCurrentPageVersionAssociation(
        db_page, db_version
    )
    db.session.add(db_current_version_association)

    db.session.commit()

    return db_page, db_version


def update_page(
    page_id: PageID,
    language_code: str,
    url_path: str,
    created_at: datetime,
    creator_id: UserID,
    title: str,
    head: str | None,
    body: str,
) -> tuple[DbPage, DbPageVersion]:
    """Update page with a new version."""
    version_id = PageVersionID(generate_uuid7())

    db_page = get_page(page_id)

    db_page.language_code = language_code
    db_page.url_path = url_path

    db_version = DbPageVersion(
        version_id, db_page, created_at, creator_id, title, head, body
    )
    db.session.add(db_version)

    db_page.current_version = db_version

    db.session.commit()

    return db_page, db_version


def delete_page(page_id: PageID) -> Result[None, PageDeletionFailedError]:
    """Delete the page and its versions.

    It is expected that no database records refer to the page anymore.
    """
    db_versions = get_versions(page_id)

    db.session.execute(
        delete(DbCurrentPageVersionAssociation).where(
            DbCurrentPageVersionAssociation.page_id == page_id
        )
    )

    for db_version in db_versions:
        db.session.execute(
            delete(DbPageVersion).where(DbPageVersion.id == db_version.id)
        )

    db.session.execute(delete(DbPage).where(DbPage.id == page_id))

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return Err(PageDeletionFailedError())

    return Ok(None)


def set_nav_menu_id(page_id: PageID, nav_menu_id: NavMenuID | None) -> None:
    """Set navigation menu for page."""
    db_page = get_page(page_id)

    db_page.nav_menu_id = nav_menu_id
    db.session.commit()


def find_page(page_id: PageID) -> DbPage | None:
    """Return the page, or `None` if not found."""
    return db.session.get(DbPage, page_id)


def get_page(page_id: PageID) -> DbPage:
    """Return the page.

    Raise error if not found.
    """
    db_page = find_page(page_id)

    if db_page is None:
        raise ValueError('Unknown page ID')

    return db_page


def find_version(version_id: PageVersionID) -> DbPageVersion | None:
    """Return the page version, or `None` if not found."""
    return db.session.get(DbPageVersion, version_id)


def get_versions(page_id: PageID) -> Sequence[DbPageVersion]:
    """Return all versions of the page, sorted from most recent to oldest."""
    return db.session.scalars(
        select(DbPageVersion)
        .filter_by(page_id=page_id)
        .order_by(DbPageVersion.created_at.desc())
    ).all()


def find_current_version_id(page_id: PageID) -> PageVersionID | None:
    """Return the ID of current version of the page."""
    return db.session.scalar(
        select(DbCurrentPageVersionAssociation.version_id).filter(
            DbCurrentPageVersionAssociation.page_id == page_id
        )
    )


def is_current_version(page_id: PageID, version_id: PageVersionID) -> bool:
    """Return `True` if the given version is the current version of the page."""
    return (
        db.session.scalar(
            select(
                db.exists()
                .where(DbCurrentPageVersionAssociation.page_id == page_id)
                .where(DbCurrentPageVersionAssociation.version_id == version_id)
            )
        )
        or False
    )


def find_current_version_for_name(
    site_id: SiteID, name: str, language_code: str
) -> DbPageVersion | None:
    """Return the current version of the page with that name and
    language code for that site.
    """
    return db.session.execute(
        select(DbPageVersion)
        .join(DbCurrentPageVersionAssociation)
        .join(DbPage)
        .filter(DbPage.site_id == site_id)
        .filter(DbPage.name == name)
        .filter(DbPage.language_code == language_code)
    ).scalar_one_or_none()


def find_current_version_for_url_path(
    site_id: SiteID, url_path: str, language_code: str
) -> DbPageVersion | None:
    """Return the current version of the page with that URL path and
    language code for that site.
    """
    return db.session.execute(
        select(DbPageVersion)
        .join(DbCurrentPageVersionAssociation)
        .join(DbPage)
        .filter(DbPage.site_id == site_id)
        .filter(DbPage.language_code == language_code)
        .filter(DbPage.url_path == url_path)
    ).scalar_one_or_none()


def get_page_names_and_url_paths(site_id: SiteID) -> Sequence[tuple[str, str]]:
    """Return the name and URL path of all pages of that site."""
    return (
        db.session.execute(
            select(DbPage.name, DbPage.url_path).filter_by(site_id=site_id)
        )
        .tuples()
        .all()
    )


def get_pages_for_site(site_id: SiteID) -> Sequence[DbPage]:
    """Return the IDs and names of all pages for that site and locale."""
    return db.session.scalars(select(DbPage).filter_by(site_id=site_id)).all()


def get_pages_for_site_with_current_versions(
    site_id: SiteID,
) -> Sequence[DbPage]:
    """Return all pages with their current versions for that site."""
    return (
        db.session.scalars(
            select(DbPage)
            .filter_by(site_id=site_id)
            .options(
                db.joinedload(DbPage.current_version_association).joinedload(
                    DbCurrentPageVersionAssociation.version
                ),
                db.joinedload(DbPage.nav_menu),
            )
        )
        .unique()
        .all()
    )


def search_pages(
    search_term: str, *, site_id: SiteID | None = None
) -> Sequence[DbPage]:
    """Search in (the latest versions of) pages."""
    stmt = (
        select(DbPage).join(DbCurrentPageVersionAssociation).join(DbPageVersion)
    )

    if site_id:
        stmt = stmt.filter(DbPage.site_id == site_id)

    stmt = stmt.filter(DbPageVersion.body.contains(search_term))

    return db.session.scalars(stmt).all()
