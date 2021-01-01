"""
byceps.blueprints.admin.board.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


BoardCategoryPermission = create_permission_enum('board_category', [
    'create',
    'update',
    'view',
])
