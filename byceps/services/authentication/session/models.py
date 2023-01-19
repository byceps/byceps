"""
byceps.services.authentication.session.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from ...user.models.user import User


@dataclass(eq=False, frozen=True)
class CurrentUser(User):
    """The current user, anonymous or logged in."""

    authenticated: bool
    permissions: frozenset[str]

    def __eq__(self, other) -> bool:
        return (other is not None) and (self.id == other.id)
