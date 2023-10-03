"""
byceps.services.guest_server.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


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
