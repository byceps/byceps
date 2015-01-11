# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_presence.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum

OrgaPresencePermission = create_permission_enum('orga_presence', [
    'list',
    'update',
])
