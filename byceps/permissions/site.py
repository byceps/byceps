"""
byceps.permissions.site
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'site',
    [
        ('create', lazy_gettext('Create sites')),
        ('update', lazy_gettext('Edit sites')),
        ('view', lazy_gettext('View sites')),
    ],
)
