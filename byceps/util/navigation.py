"""
byceps.util.navigation
~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from .authorization import has_current_user_permission


@dataclass(frozen=True)
class NavigationItem:
    endpoint: str
    label: str
    id: Optional[str]
    required_permission: Optional[str]
    icon: Optional[str]


class Navigation:
    """A navigation list.

    The order of items is the order in which they are added.
    """

    def __init__(self, title: str) -> None:
        self.title = title
        self.items: list[NavigationItem] = []

    def add_item(
        self,
        endpoint: str,
        label: str,
        *,
        id: Optional[str] = None,
        required_permission: Optional[str] = None,
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

    def get_items(self) -> list[NavigationItem]:
        """Return the navigation items the current user is allowed to see."""

        def user_has_permission(item: NavigationItem) -> bool:
            required_permission = item.required_permission
            if required_permission is None:
                return True

            return has_current_user_permission(required_permission)

        return list(filter(user_has_permission, self.items))
