"""
byceps.services.guest_server.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PartyIsOverError:
    """The party over, servers are no longer allowed to be registered."""


@dataclass(frozen=True)
class UserUsesNoTicketError:
    """The user uses no ticket for the party for which they want to
    register a guest server.
    """


@dataclass(frozen=True)
class QuantityLimitReachedError:
    """The user has already reached the maximum number of guest
    servers allowed to be registered for a party.
    """


@dataclass(frozen=True)
class AlreadyApprovedError:
    """The server has already been approved."""


@dataclass(frozen=True)
class NotApprovedError:
    """The server has not been approved."""


@dataclass(frozen=True)
class AlreadyCheckedInError:
    """The server has already been checked in."""


@dataclass(frozen=True)
class NotCheckedInError:
    """The server has not been checked in."""


@dataclass(frozen=True)
class AlreadyCheckedOutError:
    """The server has already been checked in."""
