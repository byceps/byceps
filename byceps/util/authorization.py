"""
byceps.util.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from importlib import import_module
import pkgutil

from flask import g
from flask_babel import LazyString

from ..services.authorization import service as authorization_service
from ..services.authorization.transfer.models import Permission, PermissionID
from ..typing import UserID


def load_permissions() -> None:
    """Load permissions from modules in the permissions package."""
    pkg_name = 'byceps.permissions'
    pkg_module = import_module(pkg_name)
    mod_infos = pkgutil.iter_modules(pkg_module.__path__)
    mod_names = {mod_info.name for mod_info in mod_infos}
    for mod_name in mod_names:
        import_module(f'{pkg_name}.{mod_name}')


def register_permissions(
    group: str, names_and_labels: list[tuple[str, LazyString]]
) -> None:
    """Register a permission."""
    for name, label in names_and_labels:
        permission_id = PermissionID(f'{group}.{name}')
        permission_registry.register_permission(permission_id, label)


def get_permissions_for_user(user_id: UserID) -> frozenset[str]:
    """Return the permissions this user has been granted."""
    registered_permission_ids = (
        permission_registry.get_registered_permission_ids()
    )
    user_permission_ids = authorization_service.get_permission_ids_for_user(
        user_id
    )

    # Ignore unregistered permission IDs.
    return frozenset(
        str(permission_id)
        for permission_id in registered_permission_ids
        if permission_id in user_permission_ids
    )


class PermissionRegistry:
    """A collection of valid permissions."""

    def __init__(self) -> None:
        self._permissions: dict[PermissionID, LazyString] = {}

    def register_permission(
        self, permission_id: PermissionID, label: LazyString
    ) -> None:
        """Add permission to the registry."""
        self._permissions[permission_id] = label

    def get_registered_permission_ids(self) -> frozenset[PermissionID]:
        """Return all registered permission IDs."""
        return frozenset(self._permissions.keys())

    def get_registered_permissions(self) -> frozenset[Permission]:
        """Return all registered permissions."""
        return frozenset(
            Permission(id=permission_id, title=label)
            for permission_id, label in self._permissions.items()
        )


permission_registry = PermissionRegistry()


def has_current_user_permission(permission: str) -> bool:
    """Return `True` if the current user has this permission."""
    return permission in g.user.permissions


def has_current_user_any_permission(*permissions: str) -> bool:
    """Return `True` if the current user has any of these permissions."""
    return any(map(has_current_user_permission, permissions))
