"""
byceps.blueprints.user_admin.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum


UserFlagFilter = Enum('UserFlagFilter', ['enabled', 'disabled'])


class UserStateFilter(Enum):

    none     = (None,)
    enabled  = (UserFlagFilter.enabled,)
    disabled = (UserFlagFilter.disabled,)

    def __init__(self, enabled):
        self.enabled = enabled

    @classmethod
    def find(cls, flag_filter):
        if flag_filter == UserFlagFilter.enabled:
            return cls.enabled
        elif flag_filter == UserFlagFilter.disabled:
            return cls.disabled
        else:
            return cls.none
