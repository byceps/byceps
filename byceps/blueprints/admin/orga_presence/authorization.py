"""
byceps.blueprints.admin.orga_presence.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum

OrgaPresencePermission = create_permission_enum('orga_presence', [
    'update',
    'view',
])
