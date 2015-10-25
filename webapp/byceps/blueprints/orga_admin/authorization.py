# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


OrgaBirthdayPermission = create_permission_enum('orga_birthday', [
    'list',
])


OrgaDetailPermission = create_permission_enum('orga_detail', [
    'view',
])


OrgaTeamPermission = create_permission_enum('orga_team', [
    'create',
    'delete',
    'list',
    'administrate_memberships',
])
