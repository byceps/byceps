"""
byceps.permission.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


SnippetPermission = create_permission_enum(
    'snippet',
    [
        'create',
        'update',
        'delete',
        'view',
        'view_history',
    ],
)


SnippetMountpointPermission = create_permission_enum(
    'snippet_mountpoint',
    [
        'create',
        'delete',
    ],
)
