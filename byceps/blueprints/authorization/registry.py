"""
byceps.blueprints.authorization.registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
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

    def get_enum_member(self, permission_id):
        """Return the enum that is registered for the given permission
        ID, or `None` if none is.
        """
        key, permission_name = permission_id.split('.', 1)

        enum = self.enums.get(key)
        if enum is None:
            return None

        try:
            return enum[permission_name]
        except KeyError:
            return None

    def get_enum_members(self, permission_ids):
        """Return the nums that are registered for the permission IDs.

        If no enum is found for a permission ID, it is silently ignored.
        """
        enums = (self.get_enum_member(p_id) for p_id in permission_ids)
        enums_without_none = (enum for enum in enums if enum is not None)
        return frozenset(enums_without_none)


permission_registry = PermissionRegistry()
