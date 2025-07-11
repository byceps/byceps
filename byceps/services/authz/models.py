"""
byceps.services.authz.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType


PermissionID = NewType('PermissionID', str)


RoleID = NewType('RoleID', str)


@dataclass(frozen=True, kw_only=True)
class Permission:
    id: PermissionID
    title: str


@dataclass(frozen=True, kw_only=True)
class Role:
    id: RoleID
    title: str
