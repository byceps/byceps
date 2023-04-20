"""
byceps.permissions.tourney
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authorization import register_permissions


register_permissions(
    'tourney',
    [
        ('administrate', lazy_gettext('Administrate tourneys')),
        ('view', lazy_gettext('View tourneys')),
    ],
)


register_permissions(
    'tourney_category',
    [
        ('administrate', lazy_gettext('Administrate tourney categories')),
        ('view', lazy_gettext('View tourney categories')),
    ],
)
