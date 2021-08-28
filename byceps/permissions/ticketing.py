"""
byceps.permissions.ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


TicketingPermission = create_permission_enum(
    'ticketing',
    [
        'administrate',
        'administrate_seat_occupancy',
        'checkin',
        'view',
    ],
)
