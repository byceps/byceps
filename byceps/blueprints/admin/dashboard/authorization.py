"""
byceps.blueprints.admin.dashboard.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


AdminDashboardPermission = create_permission_enum('admin_dashboard', [
    'view_global',
    'view_brand',
    'view_party',
])
