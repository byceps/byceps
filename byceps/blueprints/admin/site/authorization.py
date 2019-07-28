"""
byceps.blueprints.admin.site.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


SitePermission = create_permission_enum('site', [
    'create',
    'update',
    'view',
])
