"""
byceps.permissions.party
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import register_permissions


register_permissions(
    'party',
    [
        'create',
        'update',
        'view',
    ],
)
