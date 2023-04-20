"""
byceps.permissions.site
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authorization import register_permissions


register_permissions(
    'site',
    [
        ('create', lazy_gettext('Create sites')),
        ('update', lazy_gettext('Edit sites')),
        ('view', lazy_gettext('View sites')),
    ],
)


register_permissions(
    'site_navigation',
    [
        ('administrate', lazy_gettext('Administrate site navigation')),
    ],
)
