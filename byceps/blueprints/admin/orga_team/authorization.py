"""
byceps.blueprints.admin.orga_team.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


OrgaTeamPermission = create_permission_enum('orga_team', [
    'administrate_memberships',
    'create',
    'delete',
    'view',
])
