"""
byceps.blueprints.user_admin.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum


UserEnabledFilter = Enum('UserEnabledFilter', ['enabled', 'disabled'])


class UserStateFilter(Enum):

    none     = (None,)
    enabled  = (UserEnabledFilter.enabled,)
    disabled = (UserEnabledFilter.disabled,)

    def __init__(self, enabled):
        self.enabled = enabled

    @classmethod
    def find(cls, enabled_filter):
        if enabled_filter == UserEnabledFilter.enabled:
            return cls.enabled
        elif enabled_filter == UserEnabledFilter.disabled:
            return cls.disabled
        else:
            return cls.none
