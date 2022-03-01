"""
byceps.permissions.admin
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'admin',
    [
        ('access', lazy_gettext('Access admin area')),
        ('maintain', lazy_gettext('Carry out maintenance work')),
    ],
)
