# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


BoardTopicPermission = create_permission_enum('board_topic', [
    'create',
    'hide',
    'lock',
    'stick',
])


BoardPostingPermission = create_permission_enum('board_posting', [
    'create',
    'update',
    'hide',
])
