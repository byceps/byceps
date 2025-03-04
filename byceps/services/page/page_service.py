"""
byceps.services.page.page_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.events.page import (
    PageCreatedEvent,
    PageDeletedEvent,
    PageUpdatedEvent,
)
from byceps.services.core.events import EventSite, EventUser
from byceps.services.site import site_service
from byceps.services.site.models import Site, SiteID
from byceps.services.site_navigation.models import NavMenuID
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from .dbmodels import DbCurrentPageVersionAssociation, DbPage, DbPageVersion
from .errors import PageAlreadyExistsError, PageNotFoundError
from .models import (
    Page,
    PageAggregate,
    PageID,
    PageVersion,
    PageVersionID,
)


def copy_page(
    source_site: Site, target_site: Site, name: str, language_code: str
) -> Result[
    tuple[DbPageVersion, PageCreatedEvent],
    PageAlreadyExistsError | PageNotFoundError,
]:
    """Copy a page from one site to another."""
    version = find_current_version_for_name(source_site.id, name, language_code)
    if version is None:
        return Err(PageNotFoundError())

    target_version = find_current_version_for_name(
        target_site.id, name, language_code
    )
    if target_version is not None:
        return Err(PageAlreadyExistsError())

    creator = user_service.get_user(version.creator_id)

    db_version, event = create_page(
        target_site,
        version.page.name,
        version.page.language_code,
        version.page.url_path,
        creator,
        version.title,
        version.body,
        head=version.head,
    )

    return Ok((db_version, event))


def create_page(
    site: Site,
    name: str,
    language_code: str,
    url_path: str,
    creator: User,
    title: str,
    body: str,
    *,
    head: str | None = None,
) -> tuple[DbPageVersion, PageCreatedEvent]:
    """Create a page and its initial version."""
    db_page = DbPage(site.id, name, language_code, url_path)
    db.session.add(db_page)

    db_version = DbPageVersion(db_page, creator.id, title, head, body)
    db.session.add(db_version)

    db_current_version_association = DbCurrentPageVersionAssociation(
        db_page, db_version
    )
    db.session.add(db_current_version_association)

    db.session.commit()

    event = PageCreatedEvent(
        occurred_at=db_version.created_at,
        initiator=EventUser.from_user(creator),
        page_id=db_page.id,
        site=EventSite.from_site(site),
        page_name=db_page.name,
        language_code=db_page.language_code,
        page_version_id=db_version.id,
    )

    return db_version, event


def update_page(
    page_id: PageID,
    language_code: str,
    url_path: str,
    creator: User,
    title: str,
    head: str | None,
    body: str,
) -> tuple[DbPageVersion, PageUpdatedEvent]:
    """Update page with a new version."""
    db_page = _get_db_page(page_id)

    db_page.language_code = language_code
    db_page.url_path = url_path

    db_version = DbPageVersion(db_page, creator.id, title, head, body)
    db.session.add(db_version)

    db_page.current_version = db_version

    db.session.commit()

    site = site_service.get_site(db_page.site_id)

    event = PageUpdatedEvent(
        occurred_at=db_version.created_at,
        initiator=EventUser.from_user(creator),
        page_id=db_page.id,
        site=EventSite.from_site(site),
        page_name=db_page.name,
        language_code=db_page.language_code,
        page_version_id=db_version.id,
    )

    return db_version, event


def delete_page(
    page_id: PageID, *, initiator: User | None = None
) -> tuple[bool, PageDeletedEvent | None]:
    """Delete the page and its versions.

    It is expected that no database records refer to the page anymore.

    Return `True` on success, or `False` if an error occurred.
    """
    db_page = _get_db_page(page_id)

    # Keep values for use after page is deleted.
    site = site_service.get_site(db_page.site_id)
    page_name = db_page.name

    db_versions = _get_db_versions(page_id)

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
        return False, None

    event = PageDeletedEvent(
        occurred_at=datetime.utcnow(),
        initiator=EventUser.from_user(initiator) if initiator else None,
        page_id=page_id,
        site=EventSite.from_site(site),
        page_name=page_name,
        language_code=db_page.language_code,
    )

    return True, event


def set_nav_menu_id(page_id: PageID, nav_menu_id: NavMenuID | None) -> None:
    """Set navigation menu for page."""
    db_page = _get_db_page(page_id)

    db_page.nav_menu_id = nav_menu_id
    db.session.commit()


def find_page(page_id: PageID) -> Page | None:
    """Return the page, or `None` if not found."""
    db_page = _find_db_page(page_id)

    if db_page is None:
        return None

    return _db_entity_to_page(db_page)


def get_page(page_id: PageID) -> Page:
    """Return the page.

    Raise error if not found.
    """
    db_page = _get_db_page(page_id)

    return _db_entity_to_page(db_page)


def _find_db_page(page_id: PageID) -> DbPage | None:
    """Return the page, or `None` if not found."""
    return db.session.get(DbPage, page_id)


def _get_db_page(page_id: PageID) -> DbPage:
    """Return the page.

    Raise error if not found.
    """
    db_page = _find_db_page(page_id)

    if db_page is None:
        raise ValueError('Unknown page ID')

    return db_page


def find_version(version_id: PageVersionID) -> PageVersion | None:
    """Return the page version, or `None` if not found."""
    db_version = db.session.get(DbPageVersion, version_id)

    if db_version is None:
        return None

    return _db_entity_to_version(db_version)


def get_version(version_id: PageVersionID) -> PageVersion | None:
    """Return the page version.

    Raise error if not found.
    """
    version = find_version(version_id)

    if version is None:
        raise ValueError('Unknown version ID')

    return version


def get_versions(page_id: PageID) -> Sequence[DbPageVersion]:
    """Return all versions of the page, sorted from most recent to oldest."""
    return db.session.scalars(
        select(DbPageVersion)
        .filter_by(page_id=page_id)
        .order_by(DbPageVersion.created_at.desc())
    ).all()


def _get_db_versions(page_id: PageID) -> Sequence[DbPageVersion]:
    """Return all versions of that page, sorted from most recent to
    oldest.
    """
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


def get_url_paths_by_page_name_for_site(site_id: SiteID) -> dict[str, str]:
    """Return mapping from page names to URL paths for that site."""
    rows = (
        db.session.execute(
            select(DbPage.name, DbPage.url_path).filter_by(site_id=site_id)
        )
        .tuples()
        .all()
    )

    return dict(rows)


def get_pages_for_site(site_id: SiteID) -> Sequence[Page]:
    """Return the IDs and names of all pages for that site and locale."""
    db_pages = db.session.scalars(
        select(DbPage).filter_by(site_id=site_id)
    ).all()

    return [_db_entity_to_page(db_page) for db_page in db_pages]


def find_page_aggregate(version_id: PageVersionID) -> PageAggregate | None:
    """Return an aggregated page for that version."""
    version = get_version(version_id)
    if version is None:
        return None

    page = get_page(version.page_id)

    return PageAggregate(
        id=page.id,
        site_id=page.site_id,
        name=page.name,
        language_code=page.language_code,
        url_path=page.url_path,
        published=page.published,
        nav_menu_id=page.nav_menu_id,
        title=version.title,
        head=version.head,
        body=version.body,
    )


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
) -> Sequence[Page]:
    """Search in (the latest versions of) pages."""
    stmt = (
        select(DbPage).join(DbCurrentPageVersionAssociation).join(DbPageVersion)
    )

    if site_id:
        stmt = stmt.filter(DbPage.site_id == site_id)

    stmt = stmt.filter(DbPageVersion.body.contains(search_term))

    db_pages = db.session.scalars(stmt).all()

    return [_db_entity_to_page(db_page) for db_page in db_pages]


def _db_entity_to_page(db_page: DbPage) -> Page:
    return Page(
        id=db_page.id,
        site_id=db_page.site_id,
        name=db_page.name,
        language_code=db_page.language_code,
        url_path=db_page.url_path,
        published=db_page.published,
        nav_menu_id=db_page.nav_menu_id,
    )


def _db_entity_to_version(db_version: DbPageVersion) -> PageVersion:
    return PageVersion(
        id=db_version.id,
        page_id=db_version.page_id,
        created_at=db_version.created_at,
        creator_id=db_version.creator_id,
        title=db_version.title,
        head=db_version.head,
        body=db_version.body,
    )
