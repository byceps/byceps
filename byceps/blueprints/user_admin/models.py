"""
byceps.blueprints.user_admin.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum


UserEnabledFilter = Enum('UserEnabledFilter', ['enabled', 'disabled'])
