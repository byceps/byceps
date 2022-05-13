"""
byceps.permission.page
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'page',
    [
        ('create', lazy_gettext('Create pages')),
        ('update', lazy_gettext('Edit pages')),
        ('delete', lazy_gettext('Delete pages')),
        ('view', lazy_gettext('View pages')),
        ('view_history', lazy_gettext("View pages' history")),
    ],
)
