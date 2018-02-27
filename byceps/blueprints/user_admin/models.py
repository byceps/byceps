"""
byceps.blueprints.user_admin.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum


UserFlagFilter = Enum('UserFlagFilter', [
    'enabled',
    'disabled',
    'suspended',
])


class UserStateFilter(Enum):

    none      = (None                   , None)
    enabled   = (UserFlagFilter.enabled , None)
    disabled  = (UserFlagFilter.disabled, None)
    suspended = (None                   , True)

    def __init__(self, enabled, suspended):
        self.enabled = enabled
        self.suspended = suspended

    @classmethod
    def find(cls, flag_filter):
        if flag_filter == UserFlagFilter.enabled:
            return cls.enabled
        elif flag_filter == UserFlagFilter.disabled:
            return cls.disabled
        elif flag_filter == UserFlagFilter.suspended:
            return cls.suspended
        else:
            return cls.none
