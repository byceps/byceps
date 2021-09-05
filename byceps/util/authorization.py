"""
byceps.util.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from importlib import import_module
import pkgutil

from flask import g

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


def register_permissions(key: str, names: list[str]) -> None:
    """Register a permission."""
    for name in names:
        permission_registry.register_permission(f'{key}.{name}')


def get_permissions_for_user(user_id: UserID) -> frozenset[str]:
    """Return the permissions this user has been granted."""
    permission_ids = authorization_service.get_permission_ids_for_user(user_id)

    return permission_registry.get_registered_permissions(permission_ids)


class PermissionRegistry:
    """A collection of valid permissions."""

    def __init__(self) -> None:
        self.permissions: set[str] = set()

    def register_permission(self, permission: str) -> None:
        """Add permission to the registry."""
        self.permissions.add(permission)

    def get_registered_permissions(
        self, permission_ids: set[PermissionID]
    ) -> frozenset[str]:
        """Return the permission IDs that are registered.

        If a given permission ID is not registered, it is silently
        ignored.
        """
        return frozenset(p for p in self.permissions if p in permission_ids)


permission_registry = PermissionRegistry()


def has_current_user_permission(permission: str) -> bool:
    """Return `True` if the current user has this permission."""
    return permission in g.user.permissions


def has_current_user_any_permission(*permissions: str) -> bool:
    """Return `True` if the current user has any of these permissions."""
    return any(map(has_current_user_permission, permissions))
