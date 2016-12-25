# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticketing_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


TicketingPermission = create_permission_enum('ticketing', [
    'view',
])
