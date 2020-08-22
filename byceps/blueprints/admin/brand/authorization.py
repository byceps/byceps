"""
byceps.blueprints.admin.brand.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


BrandPermission = create_permission_enum('brand', [
    'create',
    'update',
    'view',
])
