"""
byceps.permissions.jobs
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


JobsPermission = create_permission_enum(
    'jobs',
    [
        'view',
    ],
)
