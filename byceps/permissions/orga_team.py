"""
byceps.permissions.orga_team
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authorization import register_permissions


register_permissions(
    'orga_team',
    [
        (
            'administrate_memberships',
            lazy_gettext('Administrate orga team memberships'),
        ),
        ('create', lazy_gettext('Create orga teams')),
        ('delete', lazy_gettext('Delete orga teams')),
        ('view', lazy_gettext('View orga teams')),
    ],
)
