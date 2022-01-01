"""
byceps.permissions.orga
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'orga_birthday',
    [
        ('view', lazy_gettext("View orgas' birthdays")),
    ],
)


register_permissions(
    'orga_detail',
    [
        ('view', lazy_gettext("View orgas' details")),
    ],
)
