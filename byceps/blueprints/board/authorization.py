"""
byceps.blueprints.board.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


BoardPermission = create_permission_enum('board', [
    'announce',
    'create',
    'hide',
    'update_of_others',
    'view_hidden',
])


BoardTopicPermission = create_permission_enum('board_topic', [
    'create',
    'update',
    'lock',
    'move',
    'pin',
])


BoardPostingPermission = create_permission_enum('board_posting', [
    'create',
    'update',
])
