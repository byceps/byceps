"""
byceps.blueprints.admin.party.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


PartyPermission = create_permission_enum(
    'party',
    [
        'create',
        'update',
        'view',
    ],
)
