"""
byceps.permissions.board
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


BoardPermission = create_permission_enum(
    'board',
    [
        'announce',
        'create',
        'hide',
        'update_of_others',
        'view_hidden',
    ],
)


BoardCategoryPermission = create_permission_enum(
    'board_category',
    [
        'create',
        'update',
        'view',
    ],
)


BoardTopicPermission = create_permission_enum(
    'board_topic',
    [
        'create',
        'update',
        'lock',
        'move',
        'pin',
    ],
)


BoardPostingPermission = create_permission_enum(
    'board_posting',
    [
        'create',
        'update',
    ],
)
