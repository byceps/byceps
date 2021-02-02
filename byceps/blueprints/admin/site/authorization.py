"""
byceps.blueprints.admin.site.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


SitePermission = create_permission_enum(
    'site',
    [
        'create',
        'update',
        'view',
    ],
)
