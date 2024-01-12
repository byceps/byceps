"""
byceps.permission.timetable
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'timetable',
    [
        ('administrate', lazy_gettext('Administrate timetables')),
        ('edit', lazy_gettext('Edit timetables')),
    ],
)
