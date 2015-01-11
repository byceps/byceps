# -*- coding: utf-8 -*-

"""
byceps.blueprints.snippet_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
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
