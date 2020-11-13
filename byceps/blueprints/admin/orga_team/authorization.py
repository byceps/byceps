"""
byceps.blueprints.admin.orga_team.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


OrgaTeamPermission = create_permission_enum('orga_team', [
    'administrate_memberships',
    'create',
    'delete',
    'view',
])
