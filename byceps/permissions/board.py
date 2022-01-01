"""
byceps.permissions.board
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'board',
    [
        ('announce', lazy_gettext('Make board announcements')),
        ('create', lazy_gettext('Create boards')),
        ('hide', lazy_gettext('Hide board topics and postings')),
        (
            'update_of_others',
            lazy_gettext('Edit board topics and postings by other users'),
        ),
        ('view_hidden', lazy_gettext('View hidden board topics and postings')),
    ],
)


register_permissions(
    'board_category',
    [
        ('create', lazy_gettext('Create board categories')),
        ('update', lazy_gettext('Edit board categories')),
        ('view', lazy_gettext('View board categories')),
    ],
)


register_permissions(
    'board_topic',
    [
        ('create', lazy_gettext('Create board topics')),
        ('update', lazy_gettext('Edit board topics')),
        ('lock', lazy_gettext('Lock/unlock board topics')),
        ('move', lazy_gettext('Move board topics to other categories')),
        ('pin', lazy_gettext('Pin/unpin board topics')),
    ],
)


register_permissions(
    'board_posting',
    [
        ('create', lazy_gettext('Create board postings')),
        ('update', lazy_gettext('Edit board postings')),
    ],
)
