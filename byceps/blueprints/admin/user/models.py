"""
byceps.blueprints.admin.user.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum


UserStateFilter = Enum('UserStateFilter', [
    'none',
    'uninitialized',
    'enabled',
    'disabled',
    'suspended',
    'deleted',
])
