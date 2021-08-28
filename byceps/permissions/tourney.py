"""
byceps.permissions.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


TourneyPermission = create_permission_enum(
    'tourney',
    [
        'administrate',
        'view',
    ],
)


TourneyCategoryPermission = create_permission_enum(
    'tourney_category',
    [
        'administrate',
        'view',
    ],
)
