"""
byceps.services.snippet.mountpoint_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db

from ..site.transfer.models import SiteID

from .models.mountpoint import Mountpoint
from .models.snippet import CurrentVersionAssociation, Snippet, SnippetVersion
from .transfer.models import MountpointID, SnippetID


def create_mountpoint(
    site_id: SiteID, endpoint_suffix: str, url_path: str, snippet_id: SnippetID
) -> Mountpoint:
    """Create a mountpoint."""
    mountpoint = Mountpoint(site_id, endpoint_suffix, url_path, snippet_id)

    db.session.add(mountpoint)
    db.session.commit()

    return mountpoint


def delete_mountpoint(mountpoint: Mountpoint) -> None:
    """Delete the mountpoint."""
    db.session.delete(mountpoint)
    db.session.commit()


def find_mountpoint(mountpoint_id: MountpointID) -> Optional[Mountpoint]:
    """Return the mountpoint with that id, or `None` if not found."""
    return Mountpoint.query.get(mountpoint_id)


def get_mountpoints_for_site(site_id: SiteID) -> Sequence[Mountpoint]:
    """Return all mountpoints for that site."""
    return Mountpoint.query \
        .filter_by(site_id=site_id) \
        .join(Snippet) \
        .all()

def find_current_snippet_version_for_mountpoint(
    site_id: SiteID, endpoint_suffix: str
) -> SnippetVersion:
    """Return the current version of the snippet mounted at that
    endpoint of that site, or `None` if not found.
    """
    return SnippetVersion.query \
        .join(CurrentVersionAssociation) \
        .join(Snippet) \
        .join(Mountpoint) \
        .filter(Mountpoint.site_id == site_id) \
        .filter(Mountpoint.endpoint_suffix == endpoint_suffix) \
        .one_or_none()
