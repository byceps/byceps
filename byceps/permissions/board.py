"""
byceps.permissions.board
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import register_permissions


register_permissions(
    'board',
    [
        'announce',
        'create',
        'hide',
        'update_of_others',
        'view_hidden',
    ],
)


register_permissions(
    'board_category',
    [
        'create',
        'update',
        'view',
    ],
)


register_permissions(
    'board_topic',
    [
        'create',
        'update',
        'lock',
        'move',
        'pin',
    ],
)


register_permissions(
    'board_posting',
    [
        'create',
        'update',
    ],
)
