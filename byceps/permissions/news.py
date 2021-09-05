"""
byceps.permissions.news
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import register_permissions


register_permissions(
    'news_channel',
    [
        'create',
    ],
)


register_permissions(
    'news_item',
    [
        'create',
        'publish',
        'update',
        'view',
        'view_draft',
    ],
)
