"""
byceps.util.navigation
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from ..services.authentication.session.models.current_user import CurrentUser


@dataclass(frozen=True)
class NavigationItem:
    endpoint: str
    label: str
    id: Optional[str]
    required_permission: Optional[Enum]
    icon: Optional[str]


class Navigation:
    """A navigation list.

    The order of items is the order in which they are added.
    """

    def __init__(self, title: str) -> None:
        self.title = title
        self.items: List[NavigationItem] = []

    def add_item(
        self,
        endpoint: str,
        label: str,
        *,
        id: Optional[str] = None,
        required_permission: Optional[Enum] = None,
        precondition: bool = True,
        icon: Optional[str] = None,
    ) -> object:
        """Add an item to the navigation."""
        if not precondition:
            return self

        item = NavigationItem(
            endpoint=endpoint,
            label=label,
            id=id,
            required_permission=required_permission,
            icon=icon,
        )

        self.items.append(item)
        return self

    def get_items(self, user: CurrentUser) -> List[NavigationItem]:
        """Return the navigation items the user is permitted to see."""

        def user_has_permission(item: NavigationItem) -> bool:
            required_permission = item.required_permission
            if required_permission is None:
                return True

            return user.has_permission(required_permission)

        return list(filter(user_has_permission, self.items))
