"""
byceps.blueprints.admin.ticketing.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


TicketingPermission = create_permission_enum('ticketing', [
    'administrate_seat_occupancy',
    'checkin',
    'view',
])
