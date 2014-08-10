# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


OrgaTeamPermission = create_permission_enum('OrgaTeam', [
    'list',
])
