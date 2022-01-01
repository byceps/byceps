"""
byceps.services.snippet.mountpoint_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db

from ..site.transfer.models import SiteID

from .dbmodels.mountpoint import Mountpoint as DbMountpoint
from .dbmodels.snippet import CurrentVersionAssociation, Snippet, SnippetVersion
from .transfer.models import Mountpoint, MountpointID, SnippetID


def create_mountpoint(
    site_id: SiteID, endpoint_suffix: str, url_path: str, snippet_id: SnippetID
) -> Mountpoint:
    """Create a mountpoint."""
    mountpoint = DbMountpoint(site_id, endpoint_suffix, url_path, snippet_id)

    db.session.add(mountpoint)
    db.session.commit()

    return _db_entity_to_mountpoint(mountpoint)


def delete_mountpoint(mountpoint_id: MountpointID) -> None:
    """Delete the mountpoint."""
    mountpoint = db.session.get(DbMountpoint, mountpoint_id)

    if mountpoint is None:
        raise ValueError(f"Unknown mountpoint ID '{mountpoint_id}'.")

    db.session.delete(mountpoint)
    db.session.commit()


def find_mountpoint(mountpoint_id: MountpointID) -> Optional[Mountpoint]:
    """Return the mountpoint with that id, or `None` if not found."""
    mountpoint = db.session.get(DbMountpoint, mountpoint_id)

    if mountpoint is None:
        return None

    return _db_entity_to_mountpoint(mountpoint)


def get_mountpoints_for_site(site_id: SiteID) -> set[Mountpoint]:
    """Return all mountpoints for that site."""
    mountpoints = db.session \
        .query(DbMountpoint) \
        .filter_by(site_id=site_id) \
        .all()

    return {_db_entity_to_mountpoint(mp) for mp in mountpoints}


def find_current_snippet_version_for_url_path(
    site_id: SiteID, url_path: str
) -> SnippetVersion:
    """Return the current version of the snippet mounted at that URL
    path for that site, or `None` if not found.
    """
    return db.session \
        .query(SnippetVersion) \
        .join(CurrentVersionAssociation) \
        .join(Snippet) \
        .join(DbMountpoint) \
        .filter(DbMountpoint.site_id == site_id) \
        .filter(DbMountpoint.url_path == url_path) \
        .one_or_none()


def _db_entity_to_mountpoint(entity: DbMountpoint) -> Mountpoint:
    return Mountpoint(
        entity.id,
        entity.site_id,
        entity.endpoint_suffix,
        entity.url_path,
        entity.snippet_id,
    )
