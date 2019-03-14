"""
byceps.services.snippet.mountpoint_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db

from .models.mountpoint import Mountpoint
from .models.snippet import Snippet
from .transfer.models import MountpointID, Scope


def create_mountpoint(endpoint_suffix: str, url_path: str, snippet: Snippet
                     ) -> Mountpoint:
    """Create a mountpoint."""
    mountpoint = Mountpoint(endpoint_suffix, url_path, snippet)

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


def get_mountpoints_for_scope(scope: Scope) -> Sequence[Mountpoint]:
    """Return all mountpoints for that scope."""
    return Mountpoint.query \
        .join(Snippet) \
            .filter_by(scope_type=scope.type_) \
            .filter_by(scope_name=scope.name) \
        .all()
