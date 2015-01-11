# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


BoardTopicPermission = create_permission_enum('board_topic', [
    'create',
    'update',
    'hide',
    'lock',
    'move',
    'pin',
    'view_hidden',
])


BoardPostingPermission = create_permission_enum('board_posting', [
    'create',
    'update',
    'hide',
    'view_hidden',
])
