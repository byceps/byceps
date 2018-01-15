"""
byceps.blueprints.snippet_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


MountpointPermission = create_permission_enum('mountpoint', [
    'create',
    'delete',
])


SnippetPermission = create_permission_enum('snippet', [
    'list',
    'create',
    'update',
    'view_history',
])
