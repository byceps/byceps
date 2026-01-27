"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import LazyString

from byceps.services.authz.models import PermissionID
from byceps.util.authz import PermissionRegistry


def test_select_registered_permission_ids():
    permission_jump = PermissionID('jump')
    permission_run = PermissionID('run')
    permission_unknown1 = PermissionID('unknown1')
    permission_unknown2 = PermissionID('unknown2')
    permission_unknown3 = PermissionID('unknown3')

    registry = PermissionRegistry()

    for permission_id in permission_jump, permission_run:
        registry.register_permission(
            permission_id, LazyString(str(permission_id))
        )

    assert registry.select_registered_permission_ids(
        {
            permission_unknown1,
            permission_jump,
            permission_unknown2,
            permission_run,
            permission_unknown3,
        }
    ) == {permission_jump, permission_run}
