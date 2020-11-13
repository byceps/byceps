"""
byceps.blueprints.admin.news.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


NewsChannelPermission = create_permission_enum('news_channel', [
    'create',
])


NewsItemPermission = create_permission_enum('news_item', [
    'create',
    'publish',
    'update',
    'view',
    'view_draft',
])
