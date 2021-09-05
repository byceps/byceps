"""
byceps.permission.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import register_permissions


register_permissions(
    'snippet',
    [
        'create',
        'update',
        'delete',
        'view',
        'view_history',
    ],
)


register_permissions(
    'snippet_mountpoint',
    [
        'create',
        'delete',
    ],
)
