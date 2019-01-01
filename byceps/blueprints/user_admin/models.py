"""
byceps.blueprints.user_admin.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum


UserStateFilter = Enum('UserStateFilter', [
    'none',
    'enabled',
    'disabled',
    'suspended',
    'deleted',
])
