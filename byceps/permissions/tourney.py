"""
byceps.permissions.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import register_permissions


register_permissions(
    'tourney',
    [
        'administrate',
        'view',
    ],
)


register_permissions(
    'tourney_category',
    [
        'administrate',
        'view',
    ],
)
