"""
byceps.blueprints.admin.board.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


BoardCategoryPermission = create_permission_enum('board_category', [
    'create',
    'update',
    'view',
])
