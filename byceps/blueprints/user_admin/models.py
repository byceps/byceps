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
    'deleted',
])


class UserStateFilter(Enum):

    none      = (None                   , None, None)
    enabled   = (UserFlagFilter.enabled , None, None)
    disabled  = (UserFlagFilter.disabled, None, None)
    suspended = (None                   , True, None)
    deleted   = (None                   , None, True)

    def __init__(self, enabled, suspended, deleted):
        self.enabled = enabled
        self.suspended = suspended
        self.deleted = deleted

    @classmethod
    def find(cls, flag_filter):
        if flag_filter == UserFlagFilter.enabled:
            return cls.enabled
        elif flag_filter == UserFlagFilter.disabled:
            return cls.disabled
        elif flag_filter == UserFlagFilter.suspended:
            return cls.suspended
        elif flag_filter == UserFlagFilter.deleted:
            return cls.deleted
        else:
            return cls.none
