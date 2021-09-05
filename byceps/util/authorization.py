"""
byceps.util.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from enum import Enum, EnumMeta
from importlib import import_module
import pkgutil
from typing import Optional

from flask import current_app, g

from ..services.authorization import service as authorization_service
from ..services.authorization.transfer.models import PermissionID
from ..typing import UserID


def load_permissions() -> None:
    """Load permissions from modules in the permissions package."""
    pkg_name = f'byceps.permissions'
    pkg_module = import_module(pkg_name)
    mod_infos = pkgutil.iter_modules(pkg_module.__path__)
    mod_names = {mod_info.name for mod_info in mod_infos}
    for mod_name in mod_names:
        import_module(f'{pkg_name}.{mod_name}')


def create_permission_enum(key: str, member_names: list[str]) -> EnumMeta:
    """Create a permission enum."""
    name = _derive_enum_name(key)

    permission_enum = Enum(name, list(member_names))
    permission_enum.__key__ = key
    permission_enum.__repr__ = lambda self: f'<{self}>'

    permission_registry.register_enum(permission_enum)

    return permission_enum


def _derive_enum_name(key: str) -> str:
    """Derive a `CamelCase` name from the `underscore_separated_key`."""
    words = key.split('_')
    words.append('permission')

    return ''.join(word.title() for word in words)


def get_permissions_for_user(user_id: UserID) -> frozenset[Enum]:
    """Return the permissions this user has been granted."""
    permission_ids = authorization_service.get_permission_ids_for_user(user_id)
    return permission_registry.get_enum_members(permission_ids)


class PermissionRegistry:

    def __init__(self) -> None:
        self.enums: dict[str, EnumMeta] = {}

    def register_enum(self, permission_enum: EnumMeta) -> None:
        """Add an enum to the registry."""
        self.enums[permission_enum.__key__] = permission_enum

    def get_enums(self) -> frozenset[EnumMeta]:
        """Return the registered enums."""
        return frozenset(self.enums.values())

    def get_enum_member(self, permission_id: PermissionID) -> Optional[Enum]:
        """Return the enum that is registered for the given permission
        ID, or `None` if none is.
        """
        enum_key, permission_name = permission_id.split('.', 1)

        enum = self.enums.get(enum_key)
        if enum is None:
            # No enum found for that key. This happens if the blueprint
            # which contains the authorization enum is not registered in
            # the current app mode (admin/site).
            return None

        try:
            return enum[permission_name]
        except KeyError:
            current_app.logger.warning(
                'Ignoring unknown permission name "%s" configured '
                'in database for "%s" enum (permission ID: "%s").',
                permission_name,
                enum_key,
                permission_id,
            )
            return None

    def get_enum_members(
        self, permission_ids: set[PermissionID]
    ) -> frozenset[Enum]:
        """Return the enums that are registered for the permission IDs.

        If no enum is found for a permission ID, it is silently ignored.
        """
        enums = (self.get_enum_member(p_id) for p_id in permission_ids)
        enums_without_none = (enum for enum in enums if enum is not None)
        return frozenset(enums_without_none)


permission_registry = PermissionRegistry()


def has_current_user_permission(permission: Enum) -> bool:
    """Return `True` if the current user has this permission."""
    return permission in g.user.permissions


def has_current_user_any_permission(*permissions: Enum) -> bool:
    """Return `True` if the current user has any of these permissions."""
    return any(map(has_current_user_permission, permissions))
