"""
byceps.permissions.news
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'news_channel',
    [
        ('create', lazy_gettext('Create news channels')),
    ],
)


register_permissions(
    'news_item',
    [
        ('create', lazy_gettext('Create news items')),
        ('publish', lazy_gettext('Publish news items')),
        ('update', lazy_gettext('Edit news items')),
        ('view', lazy_gettext('View news items')),
        ('view_draft', lazy_gettext('View news item drafts')),
    ],
)
