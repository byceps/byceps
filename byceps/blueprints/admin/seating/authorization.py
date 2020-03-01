"""
byceps.blueprints.admin.seating.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


SeatingPermission = create_permission_enum('seating', [
    'administrate',
    'view',
])
