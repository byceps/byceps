"""
byceps.permissions.orga_presence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


OrgaPresencePermission = create_permission_enum(
    'orga_presence',
    [
        'update',
        'view',
    ],
)
