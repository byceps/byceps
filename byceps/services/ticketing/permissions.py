"""
byceps.services.ticketing.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'ticketing',
    [
        ('administrate', lazy_gettext('Administrate ticketing')),
        (
            'administrate_seat_occupancy',
            lazy_gettext('Administrate seat occupancies'),
        ),
        ('checkin', lazy_gettext('Check in tickets')),
        ('view', lazy_gettext('View ticketing')),
    ],
)
