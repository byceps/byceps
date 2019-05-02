"""
byceps.blueprints.news_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
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
