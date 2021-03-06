"""
byceps.blueprints.admin.orga.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


OrgaBirthdayPermission = create_permission_enum('orga_birthday', [
    'view',
])


OrgaDetailPermission = create_permission_enum('orga_detail', [
    'view',
])
