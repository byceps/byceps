"""
byceps.blueprints.admin.snippet.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


SnippetMountpointPermission = create_permission_enum('snippet_mountpoint', [
    'create',
    'delete',
])


SnippetPermission = create_permission_enum('snippet', [
    'create',
    'update',
    'view',
    'view_history',
])
