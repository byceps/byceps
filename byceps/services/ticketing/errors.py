"""
byceps.services.ticketing.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TicketingError:
    """Indicate a generic ticketing error"""

    message: str


@dataclass(frozen=True)
class TicketBelongsToDifferentPartyError(TicketingError):
    """Indicate an error caused by the ticket being issued for a
    different party than the one the user is trying to check in for.
    """


@dataclass(frozen=True)
class TicketIsRevokedError(TicketingError):
    """Indicate an error caused by the ticket being revoked."""


@dataclass(frozen=True)
class TicketLacksUserError(TicketingError):
    """Indicate a (failed) attempt to check a user in with a ticket
    which has no user set.
    """


@dataclass(frozen=True)
class UserAccountDeletedError(TicketingError):
    """Indicate that an action failed because the user account has been
    deleted.
    """


@dataclass(frozen=True)
class UserAccountSuspendedError(TicketingError):
    """Indicate that an action failed because the user account is suspended."""


@dataclass(frozen=True)
class UserAlreadyCheckedInError(TicketingError):
    """Indicate that user check-in failed because a user has already
    been checked in with the ticket.
    """


@dataclass(frozen=True)
class UserIdUnknownError(TicketingError):
    """Indicate that a user ID is unknown."""


@dataclass(frozen=True)
class SeatChangeDeniedForBundledTicketError(TicketingError):
    """Indicate that the ticket belongs to a bundle and, thus, must not
    be used to occupy (or release) a single seat.
    """


@dataclass(frozen=True)
class SeatChangeDeniedForGroupSeatError(TicketingError):
    """Indicate that the seat belongs to a group and, thus, cannot be
    occupied by a single ticket that does not belong to a bundle, and
    cannot be released on its own.
    """


@dataclass(frozen=True)
class TicketCategoryMismatchError(TicketingError):
    """Indicate that the provided ticket category does not match the one
    of the target item.
    """
