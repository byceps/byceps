"""
byceps.blueprints.admin.ticketing.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


TicketingPermission = create_permission_enum('ticketing', [
    'checkin',
    'view',
])
