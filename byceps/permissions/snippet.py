"""
byceps.permission.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authorization import register_permissions


register_permissions(
    'snippet',
    [
        ('create', lazy_gettext('Create snippets')),
        ('update', lazy_gettext('Edit snippets')),
        ('delete', lazy_gettext('Delete snippets')),
        ('view', lazy_gettext('View snippets')),
        ('view_history', lazy_gettext("View snippets' history")),
    ],
)
