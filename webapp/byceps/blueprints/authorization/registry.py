# -*- coding: utf-8 -*-

"""
byceps.blueprints.authorization.registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""


class PermissionRegistry(object):

    def __init__(self):
        self.enums = {}

    def register_enum(self, permission_enum):
        """Add an enum to the registry."""
        self.enums[permission_enum.__key__] = permission_enum

    def get_enums(self):
        """Return the registered enums."""
        return frozenset(self.enums.values())

    def get_enum_member(self, permission):
        """Return the enum that is registered for the given permission
        model instance, or `None` if none is.
        """
        key, permission_name = permission.id.split('.', 1)

        enum = self.enums.get(key)
        if enum is None:
            return None

        try:
            return enum[permission_name]
        except KeyError:
            return None


permission_registry = PermissionRegistry()
