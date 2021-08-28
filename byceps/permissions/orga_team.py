"""
byceps.permissions.orga_team
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


OrgaTeamPermission = create_permission_enum(
    'orga_team',
    [
        'administrate_memberships',
        'create',
        'delete',
        'view',
    ],
)
