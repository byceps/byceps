"""
byceps.blueprints.admin.user.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum


UserStateFilter = Enum(
    'UserStateFilter',
    [
        'none',
        'active',
        'uninitialized',
        'suspended',
        'deleted',
    ],
)
