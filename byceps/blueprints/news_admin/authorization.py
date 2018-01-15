"""
byceps.blueprints.news_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


NewsItemPermission = create_permission_enum('news_item', [
    'create',
    'update',
    'list',
])
