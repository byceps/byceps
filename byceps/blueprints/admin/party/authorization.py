"""
byceps.blueprints.admin.party.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


PartyPermission = create_permission_enum('party', [
    'create',
    'update',
    'view',
])
